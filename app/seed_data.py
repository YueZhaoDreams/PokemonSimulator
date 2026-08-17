from __future__ import annotations

from app.engine.effects import parse_attack
from app.engine.models import Ability, Card

SET_A_NAMES = [
    "Bronzor",
    "Metang",
    "Orthworm",
    "Baltoy",
    "Rockruff",
    "Carbink",
    "Seel",
    "Corphish",
    "Poliwhirl",
    "Dondozo",
    "Phantump",
    "Gloom",
    "Oddish",
    "Roselia",
    "Pikachu",
    "Dusclops",
    "Flittle",
    "Kadabra",
    "Clefairy",
    "Flutter Mane",
    "Hisuian Sliggoo",
    "Psychic Energy",
    "Lake Acuity",
    "Poké Ball",
    "Ultra Ball",
    "Energy Switch",
    "Tool Box",
    "Trekking Shoes",
]

SET_B_NAMES = [
    "Ivysaur",
    "Roselia",
    "Grass Energy",
    "Tangela",
    "Sudowoodo",
    "Gible",
    "Rockruff",
    "Relicanth",
    "Salazzle",
    "Crocalor",
    "Slugma",
    "Litwick",
    "Energy Search",
    "Ferroseed",
    "Galarian Meowth",
    "Aron",
    "Energy Retrieval",
    "Gimmighoul",
    "Electrike",
    "Pikachu",
    "Plusle",
    "Emolga",
    "Wailmer",
    "Corphish",
    "Lickilicky",
    "Spinarak",
    "Aipom",
    "Tulip",
]


def _atk(name, cost, damage=0, text=""):
    return parse_attack({"name": name, "cost": cost, "damage": damage, "effect": text})


def _pkm(name, stage, types, hp, attacks, evolves_from=None, retreat=1, catalog_id=None, abilities=None, weakness=None):
    return Card(
        catalog_id=catalog_id or name.lower().replace(" ", "-"),
        name=name,
        category="Pokemon",
        stage=stage,
        types=types,
        hp=hp,
        attacks=attacks,
        abilities=abilities or [],
        weaknesses=[{"type": weakness, "value": "×2"}] if weakness else [],
        retreat=retreat,
        evolves_from=evolves_from,
    )


def _trn(name, kind, text=""):
    return Card(
        catalog_id=name.lower().replace(" ", "-"),
        name=name,
        category="Trainer",
        stage=kind.title(),
        trainer_kind=kind,
        text=text,
        retreat=0,
    )


def _nrg(energy_type: str) -> Card:
    return Card(
        catalog_id=f"energy-{energy_type.lower()}",
        name=f"{energy_type} Energy",
        category="Energy",
        stage="Basic",
        types=[energy_type],
        energy_type=energy_type,
        retreat=0,
    )


FALLBACK_BY_NAME: dict[str, Card] = {}


def _register(card: Card) -> Card:
    FALLBACK_BY_NAME[card.name.lower()] = card
    return card


_register(_trn("Hop", "supporter", "Draw 3 cards."))
_register(_trn("Youngster", "supporter", "Shuffle your hand into your deck and draw 5 cards."))
_register(_trn("Shauna", "supporter", "Shuffle your hand into your deck and draw 5 cards."))
_register(_trn("Rare Candy", "item", "Evolve a Pokémon, skipping the middle stage."))
_register(_trn("Quick Ball", "item", "Search your deck for a Pokémon."))
_register(_trn("Great Ball", "item", "Search your deck for a Pokémon."))
_register(_trn("Nest Ball", "item", "Search your deck for a Basic Pokémon."))
_register(_trn("Picnic Basket", "item", "Heal 30 damage from each of your Pokémon."))
_register(_trn("Energy Search", "item", "Search your deck for a Basic Energy card."))
_register(_trn("Energy Retrieval", "item", "Put up to 2 Basic Energy cards from your discard pile into your hand."))
_register(_trn("Energy Switch", "item", "Move a Basic Energy from 1 of your Pokémon to another of your Pokémon."))
_register(_trn("Poké Ball", "item", "Flip a coin. If heads, search your deck for a Pokémon."))
_register(_trn("Ultra Ball", "item", "Discard 2 cards from your hand. Search your deck for a Pokémon."))
_register(_trn("Tool Box", "item", "Look at the top 7 cards of your deck. You may put any Pokémon Tool cards you find there into your hand."))
_register(_trn("Trekking Shoes", "item", "Look at the top card of your deck. You may put it into your hand, or discard it and draw a card."))
_register(_trn("Lake Acuity", "stadium", "Water and Fighting Pokémon take 20 less damage from attacks."))
_register(_trn("Jacq", "supporter", "Search your deck for up to 2 Evolution Pokémon."))
_register(
    _trn(
        "Tulip",
        "supporter",
        "Put up to 4 in any combination of Psychic Pokémon and Basic Psychic Energy cards from your discard pile into your hand.",
    )
)
_register(_nrg("Psychic"))
_register(_nrg("Grass"))

for card in [
    _pkm("Sobble", "Basic", ["Water"], 60, [_atk("Water Gun", ["Water"], 20)], weakness="Lightning"),
    _pkm("Snom", "Basic", ["Water"], 50, [_atk("Powder Snow", ["Water"], 10)], weakness="Metal"),
    _pkm("Seel", "Basic", ["Water"], 70, [_atk("Headbutt", ["Water"], 20)], weakness="Lightning"),
    _pkm("Wingull", "Basic", ["Water"], 70, [_atk("Gust", ["Colorless"], 10)], weakness="Lightning"),
    _pkm("Marill", "Basic", ["Water"], 70, [_atk("Bubble Drain", ["Water", "Colorless"], 20, "Heal 20 damage from this Pokémon.")], weakness="Lightning"),
    _pkm("Dondozo", "Basic", ["Water"], 160, [
        _atk("Release Rage", ["Colorless", "Colorless"], 50, "This attack does 50 damage for each Tatsugiri in your discard pile."),
        _atk("Heavy Splash", ["Water", "Water", "Colorless", "Colorless"], 120),
    ], retreat=4, catalog_id="sv01-061", weakness="Lightning"),
    _pkm("Litten", "Basic", ["Fire"], 60, [_atk("Ember", ["Fire"], 20)], weakness="Water"),
    _pkm("Torracat", "Stage1", ["Fire"], 90, [_atk("Slash", ["Fire", "Colorless"], 50)], evolves_from="Litten", weakness="Water"),
    _pkm("Purrloin", "Basic", ["Darkness"], 60, [_atk("Scratch", ["Darkness"], 20)], weakness="Grass"),
    _pkm("Nickit", "Basic", ["Darkness"], 70, [_atk("Tail Whip", ["Darkness"], 10)], weakness="Grass"),
    _pkm("Maschiff", "Basic", ["Darkness"], 70, [_atk("Bite", ["Darkness"], 20)], weakness="Grass"),
    _pkm("Mabosstiff", "Stage1", ["Darkness"], 130, [_atk("Crunch", ["Darkness", "Darkness", "Colorless"], 100)], evolves_from="Maschiff", weakness="Grass"),
    _pkm("Bounsweet", "Basic", ["Grass"], 60, [_atk("Splash", ["Grass"], 10)], weakness="Fire"),
    _pkm("Steenee", "Stage1", ["Grass"], 90, [_atk("Razor Leaf", ["Grass", "Colorless"], 40)], evolves_from="Bounsweet", weakness="Fire"),
    _pkm("Tsareena", "Stage2", ["Grass"], 140, [_atk("Trop Kick", ["Grass", "Grass", "Colorless"], 120)], evolves_from="Steenee", weakness="Fire"),
    _pkm("Toxel", "Basic", ["Lightning"], 70, [_atk("Nuzzle", ["Lightning"], 10, "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed.")], weakness="Fighting"),
    _pkm("Tinkatink", "Basic", ["Psychic"], 70, [_atk("Smithereen", ["Colorless"], 10)], weakness="Metal"),
    _pkm("Tinkatuff", "Stage1", ["Psychic"], 90, [_atk("Heavy Smash", ["Psychic", "Colorless"], 40)], evolves_from="Tinkatink", weakness="Metal"),
    _pkm("Tinkaton", "Stage2", ["Psychic"], 140, [_atk("Hammer Launch", ["Psychic", "Psychic", "Colorless"], 120)], evolves_from="Tinkatuff", weakness="Metal"),
    _pkm("Ivysaur", "Stage1", ["Grass"], 100, [_atk("Seed Bomb", ["Grass"], 20), _atk("Leaf Whip", ["Grass", "Colorless"], 60)], evolves_from="Bulbasaur", weakness="Fire"),
    _pkm("Floragato", "Stage1", ["Grass"], 90, [_atk("Slashing Claw", ["Grass", "Colorless"], 90)], evolves_from="Sprigatito", weakness="Fire"),
    _pkm("Roselia", "Basic", ["Grass"], 70, [_atk("Bind", ["Grass"], 10, "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed."), _atk("Vine Whip", ["Grass"], 20)], weakness="Fire"),
    _pkm("Cubone", "Basic", ["Fighting"], 70, [_atk("Headbutt", ["Fighting"], 30)], weakness="Grass"),
    _pkm("Graveler", "Stage1", ["Fighting"], 110, [_atk("Rollout", ["Fighting"], 40), _atk("Rock Slide", ["Fighting", "Colorless", "Colorless"], 80)], evolves_from="Geodude", weakness="Grass"),
    _pkm("Rockruff", "Basic", ["Fighting"], 60, [_atk("Rock Kick", ["Fighting"], 20)], weakness="Grass"),
    _pkm("Salazzle", "Stage1", ["Fire"], 120, [_atk("Super Singe", ["Fire", "Colorless"], 90, "Your opponent's Active Pokémon is now Burned.")], evolves_from="Salandit", weakness="Water"),
    _pkm("Combusken", "Stage1", ["Fire"], 90, [_atk("Rolling Fireball", ["Fire", "Colorless"], 60)], evolves_from="Torchic", weakness="Water"),
    _pkm("Crocalor", "Stage1", ["Fire"], 100, [_atk("Rolling Fireball", ["Fire", "Fire"], 90, "Put an Energy attached to this Pokémon into your hand.")], evolves_from="Fuecoco", weakness="Water"),
    _pkm("Bronzor", "Basic", ["Metal"], 70, [_atk("Spinning Attack", ["Colorless"], 10)], weakness="Fire"),
    _pkm("Metang", "Stage1", ["Metal"], 100, [_atk("Bullet Punch", ["Metal"], 30)], evolves_from="Beldum", weakness="Fire"),
    _pkm("Orthworm", "Basic", ["Metal"], 140, [_atk("Punch and Draw", ["Metal"], 20)], weakness="Fire"),
    _pkm("Baltoy", "Basic", ["Fighting"], 60, [_atk("Smack", ["Fighting"], 20)], weakness="Grass"),
    _pkm("Carbink", "Basic", ["Fighting"], 90, [_atk("Lucky Find", ["Colorless"], 0), _atk("Power Gem", ["Fighting", "Fighting", "Colorless"], 80)], weakness="Grass"),
    _pkm("Poliwhirl", "Stage1", ["Water"], 90, [_atk("Light Punch", ["Water"], 30)], evolves_from="Poliwag", weakness="Lightning"),
    _pkm("Phantump", "Basic", ["Grass"], 70, [_atk("Hook", ["Grass"], 10)], weakness="Fire"),
    _pkm("Gloom", "Stage1", ["Grass"], 80, [_atk("Absorb", ["Grass"], 30)], evolves_from="Oddish", weakness="Fire"),
    _pkm("Oddish", "Basic", ["Grass"], 50, [_atk("Leaf Boomerang", ["Grass"], 10)], weakness="Fire"),
    _pkm("Dusclops", "Stage1", ["Psychic"], 90, [_atk("Fade to Black", ["Psychic"], 30, "Your opponent's Active Pokémon is now Confused.")], evolves_from="Duskull", weakness="Darkness"),
    _pkm("Flittle", "Basic", ["Psychic"], 40, [_atk("Seed Bomb", ["Psychic"], 10), _atk("Reckless Charge", ["Colorless", "Colorless"], 40)], weakness="Darkness"),
    _pkm("Kadabra", "Stage1", ["Psychic"], 80, [_atk("Teleportation Attack", ["Psychic"], 30, "Switch this Pokémon with 1 of your Benched Pokémon.")], evolves_from="Abra", weakness="Darkness"),
    _pkm("Clefairy", "Basic", ["Psychic"], 60, [_atk("Wonder Storm", ["Colorless", "Colorless", "Colorless"], 20)], weakness="Metal"),
    _pkm("Flutter Mane", "Basic", ["Psychic"], 90, [_atk("Hex Hurl", ["Psychic", "Colorless"], 90)], weakness="Metal"),
    _pkm("Hisuian Sliggoo", "Stage1", ["Dragon"], 90, [_atk("Rigidify", ["Colorless"], 0), _atk("Gentle Slap", ["Water", "Metal"], 40)], evolves_from="Goomy", weakness="Dragon"),
    _pkm("Sudowoodo", "Basic", ["Fighting"], 110, [_atk("Joust", ["Fighting"], 20)], weakness="Water"),
    _pkm("Gible", "Basic", ["Fighting"], 70, [_atk("Bite", ["Fighting"], 20)], weakness="Grass"),
    _pkm("Relicanth", "Basic", ["Fighting"], 90, [_atk("Into the Deep", ["Colorless"], 0), _atk("Tackle", ["Fighting", "Colorless"], 80)], weakness="Grass"),
    _pkm("Tangela", "Basic", ["Grass"], 80, [_atk("Beat", ["Grass"], 10), _atk("Vine Whip", ["Grass", "Grass", "Colorless"], 60)], weakness="Fire"),
    _pkm("Gimmighoul", "Basic", ["Psychic"], 50, [_atk("Call for Family", ["Colorless"], 0), _atk("Corkscrew Punch", ["Colorless", "Colorless"], 20)], weakness="Darkness"),
    _pkm("Plusle", "Basic", ["Lightning"], 70, [_atk("Plus Damage", ["Colorless", "Colorless"], 10)], weakness="Fighting"),
    _pkm("Lickilicky", "Stage1", ["Colorless"], 140, [_atk("Tongue Slap", ["Colorless"], 40), _atk("Heavy Impact", ["Colorless", "Colorless", "Colorless"], 90)], evolves_from="Lickitung", weakness="Fighting"),
    _pkm("Slugma", "Basic", ["Fire"], 70, [_atk("Flare", ["Fire"], 10), _atk("Combustion", ["Fire", "Colorless"], 30)], weakness="Water"),
    _pkm("Litwick", "Basic", ["Fire"], 60, [_atk("Searing Flame", ["Fire"], 10, "Flip a coin. If heads, your opponent's Active Pokémon is now Burned.")], weakness="Water"),
    _pkm("Ferroseed", "Basic", ["Metal"], 60, [_atk("Spike Ring", ["Metal"], 20)], weakness="Fire"),
    _pkm("Galarian Meowth", "Basic", ["Metal"], 60, [_atk("Scratch", ["Metal"], 10), _atk("Spiked Heels", ["Colorless", "Colorless"], 30)], weakness="Fire"),
    _pkm("Aron", "Basic", ["Metal"], 60, [_atk("Dig-Claws", ["Metal"], 20)], weakness="Fire"),
    _pkm("Electrike", "Basic", ["Lightning"], 60, [_atk("Thunder Fang", ["Lightning"], 20, "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed.")], weakness="Fighting"),
    _pkm("Pichu", "Basic", ["Lightning"], 30, [_atk("Mix-Up", ["Colorless"], 0, "Draw a card.")], weakness="Fighting"),
    _pkm("Emolga", "Basic", ["Lightning"], 70, [_atk("Call for Family", ["Colorless"], 0, "Search your deck for a Basic Pokémon and put it onto your Bench."), _atk("Static Shock", ["Lightning"], 40)], weakness="Fighting"),
    _pkm("Dedenne", "Basic", ["Psychic"], 70, [_atk("Call for Family", ["Colorless"], 0, "Search your deck for a Basic Pokémon."), _atk("Voltish Pulse", ["Psychic"], 30, "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed.")], weakness="Metal"),
    _pkm("Aipom", "Basic", ["Colorless"], 60, [_atk("Tail Slap", ["Colorless"], 20)], weakness="Fighting"),
    _pkm("Corphish", "Basic", ["Water"], 70, [_atk("Water Gun", ["Water"], 10), _atk("Crabhammer", ["Water", "Colorless"], 50)], weakness="Lightning"),
    _pkm("Wailmer", "Basic", ["Water"], 120, [_atk("Slap", ["Colorless"], 20), _atk("Wave Splash", ["Water", "Colorless"], 50)], weakness="Lightning"),
    _pkm("Spinarak", "Basic", ["Grass"], 60, [_atk("Poison Sting", ["Grass"], 20, "Your opponent's Active Pokémon is now Poisoned.")], weakness="Fire"),
    _pkm("Lickitung", "Basic", ["Colorless"], 90, [_atk("Tongue Slap", ["Colorless"], 30), _atk("Heavy Impact", ["Colorless", "Colorless"], 50)], weakness="Fighting"),
]:
    _register(card)

# Two Pikachu prints: family photo B has Thunder Shock (paralysis).
_register(_pkm(
    "Pikachu",
    "Basic",
    ["Lightning"],
    60,
    [
        _atk("Tail Whap", ["Colorless"], 10),
        _atk(
            "Thunder Shock",
            ["Lightning"],
            20,
            "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed.",
        ),
    ],
    catalog_id="family-pikachu-thundershock",
    weakness="Fighting",
))


def fallback_named(name: str) -> Card:
    key = name.lower()
    if key in FALLBACK_BY_NAME:
        card = FALLBACK_BY_NAME[key]
        return Card.from_dict(card.to_dict())
    if key.endswith(" energy"):
        return _nrg(name.split()[0].title())
    from app.catalog import fallback_card

    return fallback_card(name)


def build_fallback_deck(names: list[str]) -> list[Card]:
    return [fallback_named(n) for n in names]
