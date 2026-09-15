import importlib.util
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_C60_NAMES, build_fallback_deck


def _load_lab():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_c60_toolbox_swap.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


LAB = _load_lab()


def test_toolbox_trials_keep_belt_and_arven():
    rules = standard_60_rules()
    by_key = dict(LAB.variant_lists())
    assert by_key["toolbox"] == list(SET_C60_NAMES)
    assert by_key["toolbox"].count("Tool Box") == 1
    for key, names in by_key.items():
        assert len(names) == 60, key
        assert copy_violations(build_fallback_deck(names), rules) == [], key
        assert names.count("Maximum Belt") == 1, key
        assert names.count("Arven") == 1, key
        if key == "toolbox":
            continue
        assert names.count("Tool Box") == 0, key
    assert by_key["tele"].count("Telepathic Psychic Energy") == 3
    assert by_key["energy"].count("Psychic Energy") == 14
    assert by_key["boss"].count("Boss's Orders") == 4


def test_toolbox_swap_json_cells_follow_foe_order():
    import json

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-toolbox-swap.json").read_text()
    )
    foes = ["t60", "hedrick", "unl", "d60", "s60", "g", "h"]
    assert blob["games"] == 3000
    assert blob["seed"] == 20260911
    assert list(blob["foes"]) == foes
    assert list(blob["cells"])[0] == "toolbox"
    assert blob["lists"]["toolbox"] == list(SET_C60_NAMES)
    for row in blob["cells"].values():
        assert list(row) == foes
    energy = blob["cells"]["energy"]
    toolbox = blob["cells"]["toolbox"]
    assert energy["d60"]["a"] >= toolbox["d60"]["a"] - 0.01
    assert energy["hedrick"]["a"] > toolbox["hedrick"]["a"]
