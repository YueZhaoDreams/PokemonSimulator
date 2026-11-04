from app.config import STATIC_DIR


def _read(name: str) -> str:
    return (STATIC_DIR / name).read_text(encoding="utf-8")


def test_pad_shell_is_the_cards_screen():
    html = _read("index.html")
    nav = html[html.index("<nav") : html.index("</nav>")]
    assert ">Pad<" in nav
    assert 'data-view="cards"' in nav
    assert 'data-view="decks"' in html
    assert 'data-view="fight"' in html
    assert 'data-view="lab"' in html
    cards = html[html.index('id="view-cards"') : html.index('id="view-fight"')]
    assert ">Pad<" in cards
    assert 'id="padDevice"' in cards
    assert 'class="pad-portrait"' in cards
    assert 'class="pad-toolbar"' in cards
    assert 'data-mode="pokemon"' in cards
    assert 'class="pad-search"' in cards
    assert 'id="padCamera"' in cards
    assert 'aria-label="Pokémon"' in cards
    assert 'aria-label="Card"' in cards
    assert 'id="padSpeak"' in cards
    assert 'aria-label="朗读"' in cards
    assert 'id="padIdle"' in cards
    assert 'class="pad-ball"' in cards
    assert 'class="pad-pulse"' in cards
    assert "TRAINER" not in cards
    assert "081/088" not in cards
    assert 'id="cardsHost"' in cards
    assert 'id="findPanel"' in cards
    assert 'id="addName"' in cards
    assert 'id="findScan"' in cards
    assert 'id="ownedGrid"' in cards
    assert cards.index('id="padDevice"') < cards.index('id="cardsHost"')


def test_pad_shell_css_matches_the_handheld():
    css = _read("styles.css")
    assert ".pad-device" in css
    assert ".pad-red" in css
    assert ".pad-white" in css
    assert ".pad-ball" in css
    assert ".pad-pulse" in css
    assert ".pad-portrait" in css
    assert ".pad-toolbar" in css
    assert "overflow: hidden" in css
    assert "grid-template-columns: 76px" in css
    assert ".pad-idle[hidden]" in css
    assert "#padSprite[hidden]" in css
    assert ".pad-hits[hidden]" in css
    assert "(orientation: landscape)" in css
    assert "max-width: 700px" in css
    assert "(max-width: 700px) and (orientation: portrait)" in css
    assert "grid-template-columns: minmax(0, 1fr)" in css
    assert '.pad-device[data-mode="pokemon"] #cardsHost' in css
    assert '.pad-device[data-mode="card"] #padPokemon' in css


def test_pad_mode_toggle_uses_the_device():
    js = _read("app.js")
    assert "function setPadMode" in js
    assert "parkCardsPanel" in js
    assert 'dataset.mode' in js
    assert 'cardMode ? "#findScan" : "#padPhoto"' in js
    assert 'query.placeholder = next === "card"' in js
