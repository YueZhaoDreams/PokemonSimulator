from collections import Counter

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_G_FRIDAY_NAMES, SET_G_NAMES, SET_G_POFFIN_NAMES, build_fallback_deck


def _load(name: str):
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAB = _load("set_g_poffin_c60.py")


def _blob(name: str):
    import json
    from pathlib import Path

    return json.loads(
        (Path(__file__).resolve().parents[1] / "data" / "lab" / name).read_text()
    )


def test_friday_base_has_no_poffin_or_mewtwo():
    base = list(SET_G_FRIDAY_NAMES)
    assert len(base) == 60
    assert base.count("Buddy-Buddy Poffin") == 0
    assert base.count("Mewtwo ex") == 0
    assert base.count("Boss's Orders") == 3


def test_poffin_lock_is_friday_minus_four_singletons():
    locked = Counter(SET_G_POFFIN_NAMES)
    friday = Counter(SET_G_FRIDAY_NAMES)
    assert len(SET_G_POFFIN_NAMES) == 60
    assert len(SET_G_NAMES) == 60
    assert locked["Buddy-Buddy Poffin"] == 4
    assert locked["Tornadus"] == 0
    assert locked["Hop's Cramorant"] == 0
    assert locked["Relicanth"] == 0
    assert locked["Indeedee"] == 0
    assert locked["Kecleon"] == 1
    assert locked["Boss's Orders"] == 3
    assert locked["Mega Clefable ex"] == 1
    assert locked["Clefairy"] == 4
    assert friday - locked == Counter(
        {"Tornadus": 1, "Hop's Cramorant": 1, "Relicanth": 1, "Indeedee": 1}
    )
    assert locked - friday == Counter({"Buddy-Buddy Poffin": 4})
    assert copy_violations(build_fallback_deck(list(SET_G_POFFIN_NAMES)), standard_60_rules()) == []
    assert copy_violations(build_fallback_deck(list(SET_G_NAMES)), standard_60_rules()) == []


def test_poffin_packages_stay_sixty_and_legal():
    base = list(SET_G_FRIDAY_NAMES)
    for key, cuts in LAB.PACKAGES:
        names = LAB.add_poffin(base, 4, cuts)
        assert len(names) == 60, key
        assert names.count("Buddy-Buddy Poffin") == 4, key
        assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []
        for cut in cuts:
            assert Counter(names)[cut] == Counter(base)[cut] - cuts.count(cut), (key, cut)
    for cut in LAB.CUT_ONE:
        names = LAB.add_poffin(base, 1, (cut,))
        assert len(names) == 60
        assert names.count("Buddy-Buddy Poffin") == 1


def test_poffin_printed_text_matches_engine():
    from app.seed_data import fallback_named

    poffin = fallback_named("Buddy-Buddy Poffin")
    assert "up to 2 basic" in (poffin.text or "").lower()
    assert "70 hp or less" in (poffin.text or "").lower()


def test_tech_keep_kec_tops_all_field_and_noisy_screen_loses():
    blob = _blob("set-g-poffin-c60.json")
    w = blob["weighted_all"]
    assert w["tech_keep_kec"] > w["baseline"]
    assert w["tech_keep_kec"] > w["junk4"]
    assert w["tech_keep_kec"] > w["bird_thin"]
    # Singleton screen does not survive packaging: Mega/Ultra Ball/Ledian out.
    assert w["auto_top4"] < w["baseline"]
    assert blob["cells"]["auto_top4"]["c60"]["a"] < 0.15
    # Controls at the bottom.
    assert w["dark3cram"] < w["energy"]
    assert w["energy"] < w["baseline"]
    assert Counter(blob["lists"]["tech_keep_kec"])["Buddy-Buddy Poffin"] == 4
    assert Counter(blob["lists"]["tech_keep_kec"])["Tornadus"] == 0
    assert Counter(blob["lists"]["tech_keep_kec"])["Kecleon"] == 1


def test_baseline_holds_t60_across_stages_but_loses_back_half():
    blob = _blob("set-g-poffin-c60.json")
    cells = blob["cells"]
    for key, row in cells.items():
        if key == "baseline":
            continue
        assert cells["baseline"]["t60"]["a"] > row["t60"]["a"], key
    confirm = blob["confirm"]
    for key, row in confirm.items():
        if key == "baseline":
            continue
        assert confirm["baseline"]["t60"]["a"] > row["t60"]["a"], key
    # ...while Poffin accelerates the engine and takes the slow foes.
    tech = cells["tech_keep_kec"]
    base = cells["baseline"]
    assert tech["t60"]["party_games"] > base["t60"]["party_games"]
    assert tech["t60"]["gust_games"] > base["t60"]["gust_games"]
    assert tech["c60"]["a"] > base["c60"]["a"] + 0.03
    assert tech["s60"]["a"] > base["s60"]["a"]
    follow = _blob("set-g-poffin-followup.json")
    for key, row in follow["cells"].items():
        if key == "baseline":
            continue
        assert follow["cells"]["baseline"]["t60"]["a"] > row["t60"]["a"], key
    for key, row in follow["confirm"].items():
        if key == "baseline":
            continue
        assert follow["confirm"]["baseline"]["t60"]["a"] > row["t60"]["a"], key
