import json

from app.catalog import (
    _parse_search_query,
    _pretty_catalog_name,
    _read_json_list,
    lookup_seed_card,
    pick_search_hit,
    search_local,
)


def test_pretty_catalog_name_capitalizes_accented_words():
    assert _pretty_catalog_name("poké ball") == "Poké Ball"
    assert _pretty_catalog_name("Poké Ball") == "Poké Ball"
    assert _pretty_catalog_name("energy switch") == "Energy Switch"


def test_search_local_ignores_short_query():
    assert search_local("x") == []
    assert search_local(" ") == []


def test_search_hits_seed_and_energy_without_network(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: (_ for _ in ()).throw(AssertionError(q)))
    pika = search_local("pika", remote=False)
    assert "Pikachu" in [h["name"] for h in pika]
    energy = search_local("water en", remote=False)
    assert any(h["name"].lower() == "water energy" for h in energy)
    switch = search_local("energy switch", remote=False)
    assert any(h["name"] == "Energy Switch" for h in switch)
    ball = search_local("poke ball", remote=False)
    assert any(h["name"] == "Poké Ball" for h in ball)
    assert not any(h["name"] == "poké ball" for h in ball)


def test_search_local_offers_both_household_pikachu_prints(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: [])
    hits = search_local("pikachu", remote=False)
    pika = [h for h in hits if h["name"] == "Pikachu"]
    ids = {h["id"] for h in pika}
    assert "sm3-40" in ids
    assert "sm12-66" in ids
    assert hits[0]["id"] == "sm3-40"
    assert all(h.get("image") for h in pika)
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: [])
    hits = search_local("pikachu", remote=False)
    assert hits[0]["name"] == "Pikachu"


def test_search_merges_remote_cards_with_household_hits(monkeypatch):
    monkeypatch.setattr(
        "app.catalog._remote_search_briefs",
        lambda q: [{"id": "sv3pt5-4", "name": "Charmander", "image": "https://example/charmander"}],
    )
    hits = search_local("cha")
    names = [h["name"] for h in hits]
    assert "Charmander" in names
    assert "Bravery Charm" in names
    assert names.index("Charmander") < names.index("Bravery Charm")


def test_search_clefairy_line_on_clef(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: [])
    names = [h["name"] for h in search_local("clef", remote=False)]
    assert "Clefairy" in names
    assert "Clefable" in names


def test_search_remote_miss_keeps_typed_name(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: [])
    hits = search_local("zzzyxnever")
    assert hits[0]["name"] == "zzzyxnever"


def test_search_starly_reuses_legacy_name_cache(tmp_path, monkeypatch):
    monkeypatch.setattr("app.catalog.CACHE_DIR", tmp_path)
    folder = tmp_path / "http"
    folder.mkdir()
    (folder / "search-starly.json").write_text(
        json.dumps(
            [
                {"id": "swsh9-117", "name": "Starly", "localId": "117"},
                {"id": "dp1-101", "name": "Starly", "localId": "101"},
                {"id": "sm4-81", "name": "Starly", "localId": "81"},
                {"id": "swsh9-118", "name": "Staravia", "localId": "118"},
            ]
        )
    )

    def _block(*_a, **_k):
        raise AssertionError("network")

    monkeypatch.setattr("app.catalog._SEARCH_CLIENT.get", _block)
    monkeypatch.setattr("app.catalog._CLIENT.get", _block)
    hits = search_local("Starly")
    ids = [h["id"] for h in hits]
    assert "swsh9-117" in ids
    assert "dp1-101" in ids
    assert "sv01-148" in ids
    names = [h["name"] for h in hits]
    assert "Staravia" in names


def test_empty_search_cache_is_not_refetched(tmp_path, monkeypatch):
    monkeypatch.setattr("app.catalog.CACHE_DIR", tmp_path)
    from app.catalog import _search_cache_paths, _tcgdex_list_cards

    paths = _search_cache_paths([("name", "Starly")])
    paths[0].parent.mkdir(parents=True, exist_ok=True)
    paths[0].write_text("[]")

    def _block(*_a, **_k):
        raise AssertionError("network")

    monkeypatch.setattr("app.catalog._SEARCH_CLIENT.get", _block)
    monkeypatch.setattr("app.catalog._CLIENT.get", _block)
    assert _tcgdex_list_cards([("name", "Starly")]) == []


def test_search_prefix_keeps_related_names(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: [])
    names = [h["name"] for h in search_local("star", remote=False)]
    assert "Starly" in names
    assert "Staravia" in names
    assert "Staraptor" in names


def test_lookup_seed_card_falls_back_to_name_when_id_misses():
    card = lookup_seed_card("Drayton", "not-a-real-id")
    assert card is not None
    assert card.name == "Drayton"
    assert card.catalog_id == "sv08-174"


def test_read_json_list_tolerates_null_cache(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("null")
    assert _read_json_list(path) == []
    path.write_text('"nope"')
    assert _read_json_list(path) == []


def test_search_finds_seed_supporter_drayton(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: [])
    from app.catalog import _local_name_catalog

    _local_name_catalog.cache_clear()
    hits = search_local("drayton", remote=False)
    assert any(h["name"] == "Drayton" and h["id"] == "sv08-174" for h in hits)
    assert any(h.get("image") for h in hits if h["name"] == "Drayton")
    prefix = search_local("dray", remote=False)
    assert any(h["name"] == "Drayton" and h["id"] == "sv08-174" for h in prefix)


def test_search_local_finds_brilliant_stars_starly_by_collector_code(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: (_ for _ in ()).throw(AssertionError(q)))
    hits = search_local("117/172", remote=False)
    assert any(h["id"] == "swsh9-117" and h["name"] == "Starly" for h in hits)
    by_name = search_local("Starly", remote=False)
    ids = {h["id"] for h in by_name if h["name"] == "Starly"}
    assert "sv01-148" in ids
    assert "swsh9-117" in ids
    by_id = search_local("swsh9-117", remote=False)
    assert by_id[0]["id"] == "swsh9-117"


def _starly_briefs(*_a, **_k):
    others = [{"id": f"sv01-{n:03d}", "name": "Starly", "localId": str(n)} for n in range(130, 148)]
    claw = {
        "id": "swsh9-117",
        "name": "Starly",
        "localId": "117",
        "image": "https://example/starly-claw",
        "set": {"name": "Brilliant Stars", "cardCount": {"official": 172}},
    }
    return others + [claw]


def test_search_finds_collector_number_printing(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", _starly_briefs)
    hits = search_local("117/172")
    assert hits[0]["id"] == "swsh9-117"
    assert hits[0]["name"] == "Starly"
    assert hits[0]["code"] == "117/172"
    by_name_and_number = search_local("starly 117")
    assert by_name_and_number[0]["id"] == "swsh9-117"


def test_search_keeps_same_name_printings_past_default_limit(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", _starly_briefs)
    hits = search_local("Starly")
    ids = [h["id"] for h in hits if h["name"] == "Starly"]
    assert "sv01-148" in ids
    assert "swsh9-117" in ids
    assert len(ids) > 12


def test_search_collector_code_prefers_matching_set_size(monkeypatch):
    monkeypatch.setattr(
        "app.catalog._remote_search_briefs",
        lambda q: [
            {
                "id": "sv01-117",
                "name": "Grapploct",
                "localId": "117",
                "set": {"cardCount": {"official": 193}},
            },
            {
                "id": "swsh9-117",
                "name": "Starly",
                "localId": "117",
                "set": {"name": "Brilliant Stars", "cardCount": {"official": 172}},
            },
        ],
    )
    monkeypatch.setattr("app.catalog._set_official_counts", lambda: {"swsh9": "172", "sv01": "193"})
    hits = search_local("117/172")
    assert hits[0]["id"] == "swsh9-117"
    assert pick_search_hit("117/172", hits)["id"] == "swsh9-117"


def test_search_keeps_collector_hit_beyond_first_page(monkeypatch):
    crowd = [
        {"id": f"set{n}-117", "name": f"Filler{n}", "localId": "117"} for n in range(45)
    ]
    crowd.append(
        {
            "id": "swsh9-117",
            "name": "Starly",
            "localId": "117",
            "set": {"cardCount": {"official": 172}},
        }
    )
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: crowd)
    monkeypatch.setattr("app.catalog._set_official_counts", lambda: {"swsh9": "172"})
    hits = search_local("117/172")
    assert any(h["id"] == "swsh9-117" for h in hits)


def test_parse_search_query_keeps_ex_suffix_as_name():
    parsed = _parse_search_query("pikachu ex")
    assert "ex" in parsed["name"].lower()
    assert parsed["attack"] == ""
    claw = _parse_search_query("starly claw")
    assert claw["name"] == "Starly"
    assert claw["attack"] == "claw"


def test_parse_search_query_treats_round_hp_as_hp_and_collector():
    raichu = _parse_search_query("Raichu 120")
    assert raichu["name"] == "Raichu"
    assert raichu["hp"] == "120"
    assert raichu["local_id"] == "120"
    labeled = _parse_search_query("Raichu 120 hp")
    assert labeled["name"] == "Raichu"
    assert labeled["hp"] == "120"
    assert labeled["local_id"] == ""
    starly = _parse_search_query("starly 117")
    assert starly["name"] == "Starly"
    assert starly["local_id"] == "117"
    assert starly["hp"] == ""


def _many_raichu_briefs(*_a, **_k):
    crowd = [{"id": f"base1-{n}", "name": "Raichu", "localId": str(n)} for n in range(1, 46)]
    crowd.append(
        {
            "id": "swsh12-050",
            "name": "Raichu",
            "localId": "050",
            "hp": 120,
            "set": {"name": "Silver Tempest", "cardCount": {"official": 195}},
        }
    )
    crowd.append({"id": "swsh9-180", "name": "Raichu VSTAR", "localId": "180"})
    return crowd


def test_search_keeps_later_same_name_printings(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", _many_raichu_briefs)
    hits = search_local("Raichu")
    ids = [h["id"] for h in hits if h["name"] == "Raichu"]
    assert "swsh12-050" in ids
    assert len(ids) > 40


def test_search_raichu_120_hp_ranks_silver_tempest(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", _many_raichu_briefs)
    hits = search_local("Raichu 120 hp")
    assert hits[0]["id"] == "swsh12-050"
    assert pick_search_hit("Raichu 120 hp", hits)["id"] == "swsh12-050"
    by_number = search_local("Raichu 120")
    assert by_number[0]["id"] == "swsh12-050"


def test_remote_search_uses_hp_filter_not_anded_with_collector(monkeypatch):
    from app.catalog import _remote_search_briefs

    seen: list[list[tuple[str, str]]] = []

    def capture(params):
        seen.append(list(params))
        if any(key == "hp" for key, _ in params):
            return [
                {
                    "id": "swsh12-050",
                    "name": "Raichu",
                    "localId": "050",
                    "hp": 120,
                }
            ]
        return [{"id": "base1-14", "name": "Raichu", "localId": "14"}]

    monkeypatch.setattr("app.catalog._tcgdex_list_cards", capture)
    rows = _remote_search_briefs("Raichu 120 hp")
    assert any(row["id"] == "swsh12-050" for row in rows)
    assert any(("hp", "eq:120") in params for params in seen)
    assert not any(
        ("hp", "eq:120") in params and any(key == "localId" for key, _ in params) for params in seen
    )


def test_remote_search_uses_exact_collector_local_id(monkeypatch):
    from app.catalog import _remote_search_briefs

    seen: list[list[tuple[str, str]]] = []

    def capture(params):
        seen.append(list(params))
        return [
            {
                "id": "swsh9-117",
                "name": "Starly",
                "localId": "117",
                "set": {"cardCount": {"official": 172}},
            }
        ]

    monkeypatch.setattr("app.catalog._tcgdex_list_cards", capture)
    rows = _remote_search_briefs("117/172")
    assert rows[0]["id"] == "swsh9-117"
    assert any(("localId", "eq:117") in params for params in seen)
