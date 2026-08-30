from app.catalog import _pretty_catalog_name, search_local


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
