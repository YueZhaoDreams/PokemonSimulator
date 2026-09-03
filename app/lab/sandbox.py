"""Fail-closed AST gate and subprocess runner for trainer lab Python."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from subprocess import TimeoutExpired
from typing import Any

from app.config import ROOT
from app.db import save_lab_experiment
from app.engine.models import FamilyRules, default_family_rules

LAB_SCRIPT_TIMEOUT_SECONDS = 45
LAB_SCRIPT_MAX_GAMES = 400
FORBIDDEN_NAMES = frozenset(
    {
        "eval",
        "exec",
        "open",
        "compile",
        "__import__",
        "getattr",
        "setattr",
        "delattr",
        "globals",
        "locals",
        "vars",
        "dir",
        "type",
        "input",
        "breakpoint",
        "memoryview",
        "bytearray",
        "bytes",
        "object",
        "super",
        "classmethod",
        "staticmethod",
        "property",
        "help",
        "exit",
        "quit",
        "os",
        "sys",
        "subprocess",
        "socket",
        "urllib",
        "pathlib",
        "importlib",
        "pickle",
        "ctypes",
        "builtins",
        "base64",
        "shutil",
        "http",
        "requests",
        "aiohttp",
        "tempfile",
        "io",
        "inspect",
        "gc",
        "pty",
        "fcntl",
        "mmap",
        "multiprocessing",
        "threading",
        "signal",
        "code",
        "codeop",
        "runpy",
        "pkgutil",
        "types",
        "typing",
        "Game",
    }
)
FORBIDDEN_NODE_TYPES = (
    ast.Import,
    ast.ImportFrom,
    ast.AsyncFunctionDef,
    ast.AsyncFor,
    ast.AsyncWith,
    ast.Await,
    ast.Yield,
    ast.YieldFrom,
    ast.ClassDef,
    ast.Global,
    ast.Nonlocal,
    ast.With,
    ast.Match,
    ast.Delete,
)


@dataclass(frozen=True)
class ScriptVerdict:
    executable: bool
    reason: str = ""


def classify_lab_script(script_text: str | None) -> ScriptVerdict:
    if not script_text or not str(script_text).strip():
        return ScriptVerdict(False, "script is empty")
    try:
        tree = ast.parse(script_text, filename="<lab-script>")
    except SyntaxError as exc:
        return ScriptVerdict(False, f"script is not valid Python: {exc.msg}")
    try:
        _assert_safe_ast(tree)
    except ValueError as exc:
        return ScriptVerdict(False, str(exc))
    if _rebinds_run_simulation(tree):
        return ScriptVerdict(False, "script may not redefine run_simulation")
    if not _calls_run_simulation(tree):
        return ScriptVerdict(False, "script is not a Family Cup bakeoff (need run_simulation)")
    return ScriptVerdict(True)


def _name_is_run_simulation(node: ast.AST) -> bool:
    if isinstance(node, ast.Name) and node.id == "run_simulation":
        return True
    if isinstance(node, (ast.Tuple, ast.List)):
        return any(_name_is_run_simulation(item) for item in node.elts)
    return False


def _rebinds_run_simulation(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_simulation":
            return True
        if isinstance(node, ast.Assign) and any(_name_is_run_simulation(target) for target in node.targets):
            return True
        if isinstance(node, ast.AnnAssign) and _name_is_run_simulation(node.target):
            return True
        if isinstance(node, ast.For) and _name_is_run_simulation(node.target):
            return True
        if isinstance(node, ast.NamedExpr) and _name_is_run_simulation(node.target):
            return True
        if isinstance(node, ast.arg) and node.arg == "run_simulation":
            return True
    return False


def _calls_run_simulation(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "run_simulation":
            return True
    return False


def _assert_safe_ast(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN_NODE_TYPES):
            raise ValueError(f"script may not use {type(node).__name__}")
        if isinstance(node, ast.Constant) and isinstance(node.value, (bytes, bytearray)):
            raise ValueError("script must be text-only (no binary literals)")
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise ValueError(f"script may not use {node.id}")
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("_") or "__" in node.attr:
                raise ValueError("script may not use private attributes")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in FORBIDDEN_NAMES:
                raise ValueError(f"script may not call {func.id}")


def decks_payload(decks: list[dict] | dict[str, dict]) -> dict[str, dict]:
    if isinstance(decks, dict):
        items = decks.values()
    else:
        items = decks
    out: dict[str, dict] = {}
    for deck in items:
        if not isinstance(deck, dict) or not deck.get("id"):
            continue
        out[str(deck["id"])] = {
            "id": deck["id"],
            "name": deck.get("name"),
            "cards": list(deck.get("cards") or []),
        }
    return out


def run_lab_script(
    experiment: dict,
    *,
    decks: list[dict] | dict[str, dict],
    rules: FamilyRules | None = None,
    games: int | None = None,
    seed: int | None = None,
) -> dict:
    script = experiment.get("script_text")
    verdict = classify_lab_script(script)
    if not verdict.executable:
        raise ValueError(verdict.reason or "script is not executable")
    games_n = int(games if games is not None else experiment.get("games") or 200)
    seed_n = int(seed if seed is not None else experiment.get("seed") or 20260831)
    games_n = max(1, min(games_n, LAB_SCRIPT_MAX_GAMES))
    rules = rules or default_family_rules()
    payload = {
        "script": script,
        "decks": decks_payload(decks),
        "rules": rules.to_dict(),
        "games": games_n,
        "seed": seed_n,
        "queries": experiment.get("queries") or [],
        "question": experiment.get("question"),
        "cells": experiment.get("cells") or [],
        "max_games": LAB_SCRIPT_MAX_GAMES,
    }
    result = _run_in_subprocess(payload)
    if not result.get("ok"):
        raise ValueError(str(result.get("error") or "lab script failed"))
    blob = result.get("results")
    if not isinstance(blob, dict):
        raise ValueError("lab script must report a results object")
    blob.setdefault("seed", seed_n)
    blob.setdefault("games", games_n)
    return save_lab_experiment(
        owner_id=experiment["owner_id"],
        question=experiment.get("question"),
        cells=experiment.get("cells"),
        queries=experiment.get("queries"),
        games=games_n,
        seed=seed_n,
        results=blob,
        locked_cell_id=experiment.get("locked_cell_id"),
        lock_reason=experiment.get("lock_reason"),
        script_text=script,
        conclusion=experiment.get("conclusion"),
        exp_id=experiment["id"],
    )


def _run_in_subprocess(payload: dict[str, Any]) -> dict[str, Any]:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": str(ROOT),
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    with tempfile.TemporaryDirectory(prefix="lab-sandbox-") as tmp:
        env["HOME"] = tmp
        env["TMPDIR"] = tmp
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "app.lab.sandbox_worker"],
                input=json.dumps(payload).encode("utf-8"),
                capture_output=True,
                timeout=LAB_SCRIPT_TIMEOUT_SECONDS,
                cwd=tmp,
                env=env,
                check=False,
            )
        except TimeoutExpired as exc:
            raise ValueError("lab script timed out") from exc
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        out = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
        raise ValueError(err or out or f"lab sandbox exited {proc.returncode}")
    try:
        parsed = json.loads(proc.stdout.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("lab sandbox returned invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("lab sandbox returned an invalid result")
    return parsed
