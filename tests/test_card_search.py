from app.catalog import _parse_search_query, _pretty_catalog_name, pick_search_hit, search_local


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


def test_search_local_scope_does_not_touch_network(monkeypatch):
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: (_ for _ in ()).throw(AssertionError(q)))
    hits = search_local("dondozo", remote=False)
    assert hits[0]["name"] == "Dondozo"


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


def _starly_briefs(_q):
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
