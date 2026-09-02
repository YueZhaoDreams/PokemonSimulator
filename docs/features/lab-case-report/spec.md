# Lab case report

Status: in_review

Epic: open-trainer-labs

Jira Issue: TBD

## Problem And Value

The Lab tab stacked two lists and used operator-notebook words: **Experiments**, **cells**, **matrix**. Fight runs already looked like a report (question, win rates, `learning.insights`). The experiment matrix was a spreadsheet without “what we learned.” Family trainers need **one question**, a **written conclusion**, and **every run we tried** — so when Combo Cub is wrong they stay on the same case and try another version.

This slice is the Lab UX and the customer-facing API language. It does **not** start `lab-python-sandbox`.

## Scope

- Customer language: **question** / **report** / **this run** (English UI). Do not use Experiments, cells, or matrix as primary copy.
- One Lab list: questions from `lab_experiments` plus Fight `simulations` rows. Opening a question shows a report (current conclusion, then dated runs with win rates and insights), not a Strategies table.
- API and chat tools expose `attempts` and `conclusion`. Stored shape stays `lab_experiments.cells_json` + `results.cells` for compatibility.
- Each run stores `learning.insights` on the result. Question-level `conclusion` is optional trainer/chat text; if empty, the UI may show the last run’s first insight as a stand-in.
- Lab UI can open the report and **run this again** on the same question id. Full “add a run” forms can wait; Combo Cub remains the authoring path.
- Isolation unchanged: no customer Python, no git writes, no `data/lab/` from chat.

## Non-Goals

- Dispatching or implementing `lab-python-sandbox`.
- Product chat writing `data/lab/` or locking `STRATEGY_LIBRARY` into git.
- A new Python sandbox or customer-authored scripts.
- Splitting `lab_experiments` into a new table.
- A complete Lab form for every overlay field (chat can still send JSON).

## Implementation Outline

1. Spec + epic `breakdown.json` slug `lab-case-report` (depends on `lab-run-cells`).
2. `app/lab/report.py`: map cells ↔ attempts; attach attempts + conclusion on read.
3. Persist `conclusion` on `lab_experiments`; save/run/GET keep `cells` for old callers.
4. Runner copies `learning.insights` onto each run result; accept `attempts` when `cells` is empty.
5. Lab tab: unified question list + report panel; Fight runs in the same list.
6. Chat tools and `FAMILY_CUP_BRIEF` describe another run on the same question, not a multi-cell matrix.
7. Gate `lab-is-an-experiment` verify copy is the report UX. Do **not** append that gate to `passed_gates` until a human nods.

## Data Model And API Impact

- `lab_experiments.conclusion` TEXT (nullable). Existing DBs get `ALTER TABLE`.
- GET/list/save/run responses include `attempts` (id, title, input, win rates, queries, insights) and `conclusion`. `cells` remains for compatibility.
- POST/PUT and `save_lab_experiment` accept `attempts` (writes `cells_json`) and `conclusion`. If both `attempts` and `cells` are sent, `attempts` wins.
- `POST /api/lab/experiments/{id}/run` still writes `results.cells`; GET synthesizes `attempts` from cells + results.
- Chat: `list_lab_experiments`, `get_lab_experiment`, `save_lab_experiment`, `run_lab`.

## Acceptance Criteria

- [ ] A family trainer can point at the Lab tab and say which question it is, what the current conclusion is, and what the next run changed.
- [ ] English UI does not use Experiments / cells / matrix as primary labels (Question / report / this run).
- [ ] Multi-run comparison shows win rates and query rates as “what we tried,” not a spreadsheet of Cell / Strategies.
- [ ] Saving `attempts` still produces readable `cells`; old `cells` payloads still run.
- [ ] Run results include per-run insights; question `conclusion` round-trips.
- [ ] Isolation: run/save does not write `data/lab/` or `app/`.
- [ ] `lab-python-sandbox` is not started; `passed_gates` does not gain `lab-is-an-experiment` from this slice.

## Validation Plan

- Build/compile: `.venv/bin/python -m compileall app tests`
- Targeted tests: `tests/test_lab_case_report.py`, `tests/test_lab_run_cells.py`, `tests/test_lab_experiments.py`, `tests/test_ui.py`
- Broader validation: `.venv/bin/pytest -q`
- Manual review: Lab tab at `http://127.0.0.1:8000` — one question list, open report, conclusion + runs (human gate)

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
