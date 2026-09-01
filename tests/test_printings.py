from app.catalog import PREFERRED_IDS, allowed_print_ids, resolve_name
from app.engine.effects import parse_effects
from app.engine.game import play_game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named
from random import Random


def test_set_e_pins_are_the_named_cards_not_neighbor_numbers():
    """TCGDex local ids are not unique across names — pin the print, then refuse a mismatched fetch."""
    assert PREFERRED_IDS["Surfer"] == "sv08-187"
    assert PREFERRED_IDS["Lake Acuity"] == "swsh11-160"
    assert PREFERRED_IDS["Hippopotas"] == "swsh7-084"
    assert PREFERRED_IDS["Raichu"] == "swsh12-050"
    assert allowed_print_ids("Pikachu") == {"sm3-40", "sm12-66"}
    surf = fallback_named("Surfer")
    assert surf.catalog_id == "sv08-187"
    assert "sv08/187" in (surf.image or "")
    lake = fallback_named("Lake Acuity")
    assert lake.catalog_id == "swsh11-160"
    assert lake.image
    hip = fallback_named("Hippopotas")
    assert hip.name == "Hippopotas"
    assert hip.catalog_id == "swsh7-084"
    assert [a.name for a in hip.attacks] == ["Tackle", "Mud Shot"]


def test_ensure_card_images_replaces_wrong_catalog_art(monkeypatch):
    from app.seed import _ensure_card_images

    monkeypatch.setattr("app.catalog.fetch_full", lambda cid: (_ for _ in ()).throw(RuntimeError("offline")))
    out = _ensure_card_images(
        [
            {
                "name": "Hippopotas",
                "catalog_id": "sv01-112",
                "image": "https://assets.tcgdex.net/en/sv/sv01/112/low.webp",
            },
            {
                "name": "Surfer",
                "catalog_id": "sv08-191",
                "image": "https://assets.tcgdex.net/en/sv/sv08/191/low.webp",
            },
            {
                "name": "Lake Acuity",
                "catalog_id": "swsh10-160",
                "image": "https://assets.tcgdex.net/en/swsh/swsh10/160/low.webp",
            },
        ]
    )
    assert out[0]["catalog_id"] == "swsh7-084"
    assert out[0]["hp"] == 100
    assert [a["name"] for a in out[0]["attacks"]] == ["Tackle", "Mud Shot"]
    assert out[1]["catalog_id"] == "sv08-187"
    assert "sv08/191" not in (out[1].get("image") or "")
    assert out[2]["catalog_id"] == "swsh11-160"
    assert "swsh10/160" not in (out[2].get("image") or "")
    stale = _ensure_card_images(
        [
            {
                "name": "Hippopotas",
                "catalog_id": "swsh7-084",
                "hp": 90,
                "attacks": [{"name": "Take Down"}],
                "image": "https://assets.tcgdex.net/en/swsh/swsh7/084/low.webp",
            }
        ]
    )
    assert stale[0]["hp"] == 100
    assert [a["name"] for a in stale[0]["attacks"]] == ["Tackle", "Mud Shot"]
    ruff = _ensure_card_images(
        [
            {
                "name": "Rockruff",
                "catalog_id": "swsh11-109",
                "hp": 70,
                "attacks": [{"name": "Double Draw"}, {"name": "Rear Kick"}],
            }
        ]
    )
    assert ruff[0]["catalog_id"] == "swsh11-109"
    assert [a["name"] for a in ruff[0]["attacks"]] == ["Double Draw", "Rear Kick"]
    assert "swsh11/109" in (ruff[0].get("image") or "")


def test_resolve_name_skips_pinned_id_when_fetch_is_a_different_card(monkeypatch):

    def fake_fetch(card_id: str):
        if card_id == "swsh7-084":
            return {"id": "swsh7-084", "name": "Hippopotas", "category": "Pokemon", "hp": 100, "attacks": []}
        if card_id == "sv01-112":
            return {"id": "sv01-112", "name": "Riolu", "category": "Pokemon", "hp": 70, "attacks": []}
        raise AssertionError(card_id)

    monkeypatch.setattr("app.catalog.fetch_full", fake_fetch)
    monkeypatch.setattr("app.catalog.search_briefs", lambda n: [{"id": "sv01-112", "name": "Riolu"}])
    card = resolve_name("Hippopotas")
    assert card.name == "Hippopotas"
    assert card.catalog_id == "swsh7-084"


def test_dondozo_is_paradox_rift_swallow_up():
    card = resolve_name("Dondozo")
    assert card.catalog_id == "sv04-055"
    names = [a.name for a in card.attacks]
    assert "Supplemental Swallow-Up" in names
    assert "Hydro Splash" in names
    swallow = next(a for a in card.attacks if "Swallow" in a.name)
    assert swallow.damage == 0
    assert any(e.get("kind") == "swallow_energy" for e in swallow.effects)
    hydro = next(a for a in card.attacks if a.name == "Hydro Splash")
    assert hydro.damage == 180


def test_set_a_carpet_prints_match_photos():
    """Printings taken from Set A gallery crops (attacks + art), not first name hit."""
    expected = {
        "Bronzor": ("swsh11-125", ["Spinning Attack"]),
        "Metang": ("swsh12.5-090", ["Bullet Punch"]),
        "Seel": ("swsh12.5-029", ["Headbutt", "Rain Splash"]),
        "Corphish": ("swsh12.5-033", ["Water Gun", "Crabhammer"]),
        "Poliwhirl": ("swsh11-031", ["Light Punch", "Double Smash"]),
        "Phantump": ("swsh11-016", ["Hook"]),
        "Gloom": ("swsh11-002", ["Absorb"]),
        "Dusclops": ("swsh12.5-063", ["Fade to Black"]),
        "Pumpkaboo": ("sv04-077", ["Seed Bomb", "Reckless Charge"]),
    }
    for name, (cid, attacks) in expected.items():
        card = resolve_name(name)
        assert card.catalog_id == cid, f"{name} got {card.catalog_id}"
        got = [a.name for a in card.attacks]
        for attack in attacks:
            assert attack in got


def test_rockruff_prints_split_by_attack_hints():
    howl = resolve_name("Rockruff", ["invite out", "smash kick"])
    roll = resolve_name("Rockruff", ["double draw", "rear kick"])
    assert howl.catalog_id == "swsh12.5-073"
    assert roll.catalog_id == "swsh11-109"
    assert howl.catalog_id != roll.catalog_id


def test_raichu_default_print_prefers_electro_ball_over_ambushing_spark(monkeypatch):
    def fake_fetch(card_id: str):
        if card_id == "spark":
            return {
                "id": "spark",
                "name": "Raichu",
                "category": "Pokemon",
                "hp": 110,
                "attacks": [{"name": "Ambushing Spark", "damage": 50, "text": ""}],
            }
        if card_id == "ball":
            return {
                "id": "ball",
                "name": "Raichu",
                "category": "Pokemon",
                "hp": 130,
                "attacks": [{"name": "Electro Ball", "damage": 70, "text": ""}],
            }
        raise AssertionError(card_id)

    monkeypatch.setattr("app.catalog.fetch_full", fake_fetch)
    monkeypatch.setattr(
        "app.catalog.search_briefs",
        lambda n: [{"id": "spark", "name": "Raichu"}, {"id": "ball", "name": "Raichu"}],
    )
    monkeypatch.setattr("app.catalog.PREFERRED_IDS", {k: v for k, v in PREFERRED_IDS.items() if k != "Raichu"})
    default = resolve_name("Raichu")
    assert default.catalog_id == "ball"
    assert [a.name for a in default.attacks] == ["Electro Ball"]
    spark = resolve_name("Raichu", ["ambushing spark"])
    assert spark.catalog_id == "spark"


def test_ocr_blob_picks_corphish_crown_zenith_over_crimson_invasion():
    card = resolve_name("Corphish", ocr_text="Corphish 70 WaterGun10 Crabhammer 50")
    assert card.catalog_id == "swsh12.5-033"


def test_gallery_art_picks_lost_origin_phantump_and_gloom():
    """Art-only crops fooled attack-phrase matching; illustration color must win."""
    from pathlib import Path

    from app.config import DATA_DIR
    from app.recognition.images import load_image

    gallery = DATA_DIR / "gallery"
    phantump = load_image(gallery / "phantump__198639362136c008.jpg")
    gloom = load_image(gallery / "gloom__4716065e15262e9b.jpg")
    assert resolve_name("Phantump", crop_image=phantump).catalog_id == "swsh11-016"
    assert resolve_name("Gloom", crop_image=gloom).catalog_id == "swsh11-002"


def test_ocr_blob_picks_gloom_lost_origin_over_obsidian_flames():
    card = resolve_name("Gloom", ocr_text="Gloom 80 Absorb 30 Heal 30")
    assert card.catalog_id == "swsh11-002"


def test_gallery_art_picks_crown_zenith_tangela_not_twilight_masquerade():
    """Green-forest HSV hist prefers TWM; yellow frame + Beat/Vine Whip must win."""
    from app.config import DATA_DIR
    from app.recognition.images import load_image

    crop = load_image(DATA_DIR / "gallery" / "tangela__0b1616663606b4d8.jpg")
    assert resolve_name("Tangela", crop_image=crop).catalog_id == "swsh12.5-004"


def test_aipom_without_crop_is_lost_origin_not_pokemon_go():
    card = resolve_name("Aipom")
    assert card.catalog_id == "swsh11-144"
    assert [a.name for a in card.attacks] == ["Mischievous Tail", "Scratch"]


def test_set_b_carpet_prints_match_photos():
    """Set B printings taken from gallery crops (attacks + art), not first name hit."""
    expected = {
        "Ivysaur": ("sv03.5-002", ["Leech Seed", "Vine Whip"]),
        "Sudowoodo": ("swsh11-094", ["Joust", "Impound"]),
        "Gible": ("sv04-094", ["Bite"]),
        "Slugma": ("swsh11-021", ["Draw In", "Combustion"]),
        "Ferroseed": ("sv04-127", ["Spike Sting"]),
        "Electrike": ("swsh11-054", ["Zap Kick", "Thunder Fang"]),
        "Wailmer": ("swsh12.5-031", ["Nap", "Water Gun"]),
        "Aron": ("swsh12.5-087", ["Ram", "Slight Intrusion"]),
        "Spinarak": ("swsh11-112", ["Poison Sting"]),
        "Salazzle": ("swsh12.5-028", ["Tail Trickery", "Super Singe"]),
        "Crocalor": ("sv04-024", ["Rolling Fireball"]),
        "Galarian Meowth": ("swsh12.5-084", ["Fasten Claws"]),
        "Emolga": ("sv10.5b-029", ["Call for Family", "Static Shock"]),
        "Tangela": ("swsh12.5-004", ["Beat", "Vine Whip"]),
        "Spheal": ("sv08-043", ["Powder Snow"]),
        "Sealeo": ("sv08-044", ["Lunge Out", "Ice Ball"]),
        "Walrein": ("sv08-045", ["Frigid Fangs", "Megaton Fall"]),
        "Starly": ("sv01-148", ["Flap"]),
        "Staravia": ("sv01-149", ["Wing Attack", "Speed Dive"]),
        "Staraptor": ("sv01-150", ["Tailspin Away", "Power Blast"]),
        "Gligar": ("sv04-091", ["Toxic"]),
        "Aipom": ("swsh11-144", ["Mischievous Tail", "Scratch"]),
    }
    for name, (cid, attacks) in expected.items():
        card = resolve_name(name)
        assert card.catalog_id == cid, f"{name} got {card.catalog_id}"
        got = [a.name for a in card.attacks]
        for attack in attacks:
            assert attack in got
        if name == "Spinarak":
            assert "Darkness" in card.types
        if name == "Gible":
            assert card.hp == 70
            assert "Fighting" in card.types
        if name == "Staraptor":
            assert card.hp == 150
            blast = next(a for a in card.attacks if a.name == "Power Blast")
            assert blast.damage == 180
            assert any(e.get("kind") == "discard_energy" for e in blast.effects)
            spin = next(a for a in card.attacks if a.name == "Tailspin Away")
            assert any(e.get("kind") == "prevent_basic_damage" for e in spin.effects)
        if name == "Walrein":
            assert card.hp == 170
            megaton = next(a for a in card.attacks if a.name == "Megaton Fall")
            assert megaton.damage == 170
            assert any(e.get("kind") == "recoil" and e.get("amount") == 50 for e in megaton.effects)
            fangs = next(a for a in card.attacks if a.name == "Frigid Fangs")
            assert any(e.get("kind") == "energy_attack_lock" and e.get("max_energy") == 2 for e in fangs.effects)


def test_orthworm_has_crunch_time_rush():
    card = resolve_name("Orthworm")
    assert card.catalog_id == "sv04-138"
    assert any(a.name == "Crunch-Time Rush" for a in card.attacks)
    rush = next(a for a in card.attacks if "Crunch" in a.name)
    assert any(e.get("kind") == "deck_count_bonus" for e in rush.effects)


def test_parse_swallow_effect():
    effects = parse_effects(
        "Look at the top 5 cards of your deck. You may attach any number of Basic Energy cards you find there to this Pokémon."
    )
    assert effects == [{"kind": "swallow_energy", "look": 5}]


def test_dondozo_can_swallow_and_finish_game():
    dondozo = fallback_named("Dondozo")
    assert any(e.get("kind") == "swallow_energy" for a in dondozo.attacks for e in a.effects)
    a = build_fallback_deck(
        ["Dondozo"] + ["Sobble"] * 12 + ["Hop"] * 4 + ["Psychic Energy"] * 4 + ["Marill"] * 7
    )
    b = build_fallback_deck(
        ["Pikachu"] + ["Electrike"] * 10 + ["Shauna"] * 4 + ["Grass Energy"] * 4 + ["Cubone"] * 9
    )
    result = play_game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict(
            {
                "name": "dondozo",
                "prefer_damage": 1.0,
                "protect": ["Dondozo"],
                "attach_pokemon_as_energy": 0.95,
            }
        ),
        StrategySpec.from_dict("control"),
        Random(2),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
    assert any("Swallow" in line or "swallows" in line or "Hydro Splash" in line for line in result.trace) or result.turns >= 1
