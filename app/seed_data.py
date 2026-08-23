from __future__ import annotations

from app.engine.effects import parse_attack
from app.engine.models import Ability, Card

# Carpet Set A — 30 from the Aug 22 beige-carpet photo (not data/samples/set-a.jpg).
# Paldea Evolved Starly line + Twilight Masquerade Boomerang Energy. Ghosts / Clefairy / Trekking out.
# Two Psychic Energy complete the 30; the layout photo was counted as 28.
SET_A_NAMES = [
    "Lake Acuity",
    "Tulip",
    "Ultra Ball",
    "Energy Switch",
    "Poké Ball",
    "Flutter Mane",
    "Gligar",
    "Staraptor",
    "Orthworm",
    "Dondozo",
    "Carbink",
    "Oddish",
    "Staravia",
    "Bronzor",
    "Water Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Baltoy",
    "Roselia",
    "Starly",
    "Metang",
    "Poliwhirl",
    "Rockruff",
    "Aipom",
    "Metal Energy",
    "Corphish",
    "Boomerang Energy",
    "Aron",
    "Ferroseed",
    "Galarian Meowth",
]

# Carpet Set B — 30 from the Aug 22 beige-carpet photo (not data/samples/set-b.jpg).
# Surging Sparks Spheal / Sealeo / Walrein + two Pikachu prints. Fire / Darkness / Gimmighoul out.
# 4 Lightning, 3 Grass, 2 Water. Trekking Shoes in. Gimmighoul sits in spare.
SET_B_NAMES = [
    "Trekking Shoes",
    "Plusle",
    "Emolga",
    "Pikachu",  # Cosmic Eclipse Nuzzle / Volt Tackle, received from Set A for Tulip
    "Electrike",
    "Pikachu",  # Burning Shadows Tail Whap / Thunder Shock
    "Lightning Energy",
    "Lightning Energy",
    "Lightning Energy",
    "Lightning Energy",
    "Energy Retrieval",
    "Gible",
    "Rockruff",
    "Sudowoodo",
    "Relicanth",
    "Energy Search",
    "Roselia",
    "Grass Energy",
    "Ivysaur",
    "Tangela",
    "Grass Energy",
    "Grass Energy",
    "Spheal",
    "Sealeo",
    "Walrein",
    "Water Energy",
    "Seel",
    "Wailmer",
    "Water Energy",
    "Corphish",
]

# Set C — Clefairy / Mewtwo vs Charm Ogerpon. 30: 4 Clefable (name cap) + 1 Psychic Energy
# + Boss's Orders. Clefable / Clefable ex / Mega Clefable ex are different names (4 each).
# TWM/CLC Clefable share the Clefable name and cannot be a 5th copy. Maximum Belt is ACE SPEC.
# Tool Box tutors it from the top 7; Arven is the full-deck Tool + Item search.
# Moon-Watching Party is LOR 62 full-deck search.
SET_C_NAMES = (
    ["Clefairy"] * 4
    + ["Mewtwo ex"] * 2
    + ["Clefable"] * 4
    + ["Clefable ex"] * 4
    + ["Mega Clefable ex"] * 3
    + ["Hop"] * 3
    + ["Nest Ball"] * 2
    + ["Energy Search"] * 3
    + ["Maximum Belt"]
    + ["Tool Box"]
    + ["Arven"]
    + ["Boss's Orders"]
    + ["Psychic Energy"]
)

SET_D_NAMES = (  # 30: Fighting Energy 6 → 8
    ["Cornerstone Mask Ogerpon ex"] * 4
    + ["Fighting Energy"] * 8
    + ["Double Colorless Energy"] * 4
    + ["Energy Search"] * 4
    + ["Nest Ball"] * 4
    + ["Bravery Charm"] * 2
    + ["Acerola"] * 2
    + ["Switch"] * 2
)

# Set S — Grass hunter vs Charm Ogerpon. 30.
# Floragato Slashing Claw 90 + Maximum Belt 50 = 140, Grass Weakness ×2 = 280.
# Wo-Chien ex (Grass, no Ability, HP 230) is the Demolish sponge; Forest Blast 220
# also hits through Stance (×2 = 440). Paradox Rift Mewtwo is Lightning and cannot
# pay Photon in a Grass list.
SET_S_NAMES = (
    ["Sprigatito"] * 4
    + ["Floragato"] * 4
    + ["Wo-Chien ex"] * 3
    + ["Nest Ball"] * 4
    + ["Energy Search"] * 3
    + ["Switch"] * 3
    + ["Jacq"]
    + ["Maximum Belt"]
    + ["Tool Box"]
    + ["Arven"]
    + ["Hop"]
    + ["Tangela"] * 2
    + ["Grass Energy"] * 2
)

# Set T — official 30-card constructed (max 2 copies except basic Energy, 3 prizes).
# Compressed August 2026 Standard Dragapult ex (Phantom Dive) half-deck.
SET_T_NAMES = (
    ["Dreepy"] * 2
    + ["Drakloak"] * 2
    + ["Dragapult ex"] * 2
    + ["Fezandipiti ex"]
    + ["Budew"]
    + ["Lillie's Determination"] * 2
    + ["Boss's Orders"] * 2
    + ["Crispin"]
    + ["Ultra Ball"] * 2
    + ["Buddy-Buddy Poffin"] * 2
    + ["Poké Pad"] * 2
    + ["Crushing Hammer"] * 2
    + ["Night Stretcher"]
    + ["Rare Candy"]
    + ["Unfair Stamp"]
    + ["Judge"]
    + ["Psychic Energy"] * 2
    + ["Fire Energy"] * 2
    + ["Darkness Energy"]
)

# Spare Cards — leftover pile, not a 30-card Family Cup list.
# Aipom returned to Carpet Set A with the Starly line.
SET_SPARE_NAMES = [
    "Tool Box",
    "Lickilicky",
    "Fighting Energy",
    "Gimmighoul",
]


def _atk(name, cost, damage=0, text=""):
    return parse_attack({"name": name, "cost": cost, "damage": damage, "effect": text})


def _pkm(name, stage, types, hp, attacks, evolves_from=None, retreat=1, catalog_id=None, abilities=None, weakness=None, image=None, set_name=None, resistances=None):
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
        resistances=list(resistances) if resistances else [],
        retreat=retreat,
        evolves_from=evolves_from,
        image=image,
        set_name=set_name,
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
    from app.catalog import energy_card

    return energy_card(energy_type)


FALLBACK_BY_NAME: dict[str, Card] = {}


def _register(card: Card) -> Card:
    FALLBACK_BY_NAME[card.name.lower()] = card
    return card


_register(_trn("Hop", "supporter", "Draw 3 cards."))
_register(_trn("Youngster", "supporter", "Shuffle your hand into your deck and draw 5 cards."))
_register(_trn("Shauna", "supporter", "Shuffle your hand into your deck and draw 5 cards."))
_register(
    _trn(
        "Professor's Research",
        "supporter",
        "Discard your hand and draw 7 cards.",
    )
)
_register(_trn("Rare Candy", "item", "Evolve a Pokémon, skipping the middle stage."))
_register(_trn("Quick Ball", "item", "Search your deck for a Pokémon."))
_register(_trn("Great Ball", "item", "Search your deck for a Pokémon."))
_register(_trn("Nest Ball", "item", "Search your deck for a Basic Pokémon and put it onto your Bench. Then, shuffle your deck."))
_register(_trn("Picnic Basket", "item", "Heal 30 damage from each of your Pokémon."))
_register(_trn("Energy Search", "item", "Search your deck for a Basic Energy card."))
_register(_trn("Switch", "item", "Switch your Active Pokémon with 1 of your Benched Pokémon."))
_register(
    _trn(
        "Buddy-Buddy Poffin",
        "item",
        "Search your deck for up to 2 Basic Pokémon with 70 HP or less and put them onto your Bench. Then, shuffle your deck.",
    )
)
_register(
    _trn(
        "Maximum Belt",
        "item",
        "Attacks used by the Pokémon this card is attached to do 50 more damage to your opponent's Active Pokémon ex (before applying Weakness and Resistance).",
    )
)
_register(
    _trn(
        "Muscle Band",
        "item",
        "The attacks of the Pokémon this card is attached to do 20 more damage to your opponent's Active Pokémon (before applying Weakness and Resistance).",
    )
)
_register(_trn("Bravery Charm", "item", "The Basic Pokémon this card is attached to gets +50 HP."))
_register(_trn("Beach Court", "stadium", "The Retreat Cost of each Basic Pokémon in play (both yours and your opponent's) is Colorless less."))
_register(_trn("Arven", "supporter", "Search your deck for an Item card and a Pokémon Tool card, reveal them, and put them into your hand. Then, shuffle your deck."))
_register(
    _trn(
        "Acerola",
        "supporter",
        "Put 1 of your Pokémon that has any damage counters on it and all cards attached to it into your hand.",
    )
)
_register(_trn("Energy Retrieval", "item", "Put up to 2 Basic Energy cards from your discard pile into your hand."))
_register(_trn("Energy Switch", "item", "Move a Basic Energy from 1 of your Pokémon to another of your Pokémon."))
_register(
    _trn(
        "Super Rod",
        "item",
        "Shuffle up to 3 in any combination of Pokémon and Basic Energy cards from your discard pile into your deck.",
    )
)
_register(
    _trn(
        "Earthen Vessel",
        "item",
        "Search your deck for up to 2 Basic Energy cards, reveal them, and put them into your hand. Then, shuffle your deck. You must discard a card from your hand in order to use this.",
    )
)
_register(_trn("Poké Ball", "item", "Flip a coin. If heads, search your deck for a Pokémon."))
_register(_trn("Ultra Ball", "item", "Discard 2 cards from your hand. Search your deck for a Pokémon."))
_register(_trn("Tool Box", "item", "Look at the top 7 cards of your deck. You may put any Pokémon Tool cards you find there into your hand."))
_register(_trn("Trekking Shoes", "item", "Look at the top card of your deck. You may put it into your hand, or discard it and draw a card."))
_register(_trn("Lake Acuity", "stadium", "Water and Fighting Pokémon take 20 less damage from attacks."))
_register(_trn("Jacq", "supporter", "Search your deck for up to 2 Evolution Pokémon."))
_register(
    _trn(
        "Lillie's Determination",
        "supporter",
        "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead.",
    )
)
_register(_trn("Boss's Orders", "supporter", "Switch in 1 of your opponent's Benched Pokémon to the Active Spot."))
_register(
    _trn(
        "Crispin",
        "supporter",
        "Search your deck for up to 2 Basic Energy cards of different types, reveal them, and put 1 of them into your hand. Attach the other to 1 of your Pokémon. Then, shuffle your deck.",
    )
)
_register(
    _trn(
        "Poké Pad",
        "item",
        "Search your deck for a Pokémon that doesn't have a Rule Box, reveal it, and put it into your hand. Then, shuffle your deck. (Pokémon ex, Pokémon V, etc. have Rule Boxes.)",
    )
)
_register(
    _trn(
        "Crushing Hammer",
        "item",
        "Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon.",
    )
)
_register(
    _trn(
        "Night Stretcher",
        "item",
        "Put a Pokémon or a Basic Energy card from your discard pile into your hand.",
    )
)
_register(
    _trn(
        "Unfair Stamp",
        "item",
        "You can use this card only if any of your Pokémon were Knocked Out during your opponent's last turn.\n\nEach player shuffles their hand into their deck. Then, you draw 5 cards, and your opponent draws 2 cards.",
    )
)
_register(
    _trn(
        "Judge",
        "supporter",
        "Each player shuffles their hand into their deck and draws 4 cards.",
    )
)
_register(
    _trn(
        "Tulip",
        "supporter",
        "Put up to 4 in any combination of Psychic Pokémon and Basic Psychic Energy cards from your discard pile into your hand.",
    )
)
_register(_nrg("Psychic"))
_register(_nrg("Grass"))
_register(_nrg("Fighting"))
_register(_nrg("Darkness"))
_register(_nrg("Metal"))
_register(_nrg("Water"))
_register(_nrg("Lightning"))
_register(_nrg("Fire"))
_register(
    Card(
        catalog_id="sm1-136",
        name="Double Colorless Energy",
        category="Energy",
        stage="Special",
        types=["Colorless"],
        energy_type="Colorless",
        text="Double Colorless Energy provides ColorlessColorless Energy.",
        image="https://assets.tcgdex.net/en/sm/sm1/136/low.webp",
        set_name="Sun & Moon",
        retreat=0,
    )
)
_register(
    Card(
        catalog_id="sv06-166",
        name="Boomerang Energy",
        category="Energy",
        stage="Special",
        types=["Colorless"],
        energy_type="Colorless",
        text=(
            "As long as this card is attached to a Pokémon, it provides Colorless Energy. "
            "If this card is discarded by an effect of an attack used by the Pokémon this card "
            "is attached to, attach this card from your discard pile to that Pokémon after attacking."
        ),
        image="https://assets.tcgdex.net/en/sv/sv06/166/low.webp",
        set_name="Twilight Masquerade",
        retreat=0,
    )
)

for card in [
    _pkm("Sobble", "Basic", ["Water"], 60, [_atk("Water Gun", ["Water"], 20)], weakness="Lightning"),
    _pkm("Snom", "Basic", ["Water"], 50, [_atk("Powder Snow", ["Water"], 10)], weakness="Metal"),
    _pkm("Seel", "Basic", ["Water"], 70, [
        _atk("Headbutt", ["Water"], 10),
        _atk("Rain Splash", ["Water", "Colorless"], 20),
    ], catalog_id="swsh12.5-029", weakness="Lightning"),
    _pkm("Wingull", "Basic", ["Water"], 70, [_atk("Gust", ["Colorless"], 10)], weakness="Lightning"),
    _pkm("Marill", "Basic", ["Water"], 70, [_atk("Bubble Drain", ["Water", "Colorless"], 20, "Heal 20 damage from this Pokémon.")], weakness="Lightning"),
    _pkm("Dondozo", "Basic", ["Water"], 160, [
        _atk(
            "Supplemental Swallow-Up",
            ["Colorless"],
            0,
            "Look at the top 5 cards of your deck. You may attach any number of Basic Energy cards you find there to this Pokémon. Shuffle the other cards back into your deck.",
        ),
        _atk("Hydro Splash", ["Water", "Colorless", "Colorless", "Colorless", "Colorless"], 180),
    ], retreat=4, catalog_id="sv04-055", weakness="Lightning"),
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
    _pkm("Ivysaur", "Stage1", ["Grass"], 100, [
        _atk("Leech Seed", ["Grass", "Colorless"], 30, "Heal 20 damage from this Pokémon."),
        _atk("Vine Whip", ["Grass", "Grass", "Colorless"], 80),
    ], evolves_from="Bulbasaur", weakness="Fire", catalog_id="sv03.5-002"),
    _pkm(
        "Sprigatito",
        "Basic",
        ["Grass"],
        60,
        [_atk("Scratch", ["Colorless"], 10), _atk("Leafage", ["Grass"], 20)],
        weakness="Fire",
        catalog_id="sv01-013",
        image="https://assets.tcgdex.net/en/sv/sv01/013/low.webp",
        set_name="Paldea Evolved",
    ),
    _pkm(
        "Floragato",
        "Stage1",
        ["Grass"],
        90,
        [_atk("Slashing Claw", ["Grass", "Colorless"], 90)],
        evolves_from="Sprigatito",
        weakness="Fire",
        catalog_id="sv01-014",
        image="https://assets.tcgdex.net/en/sv/sv01/014/low.webp",
        set_name="Paldea Evolved",
    ),
    _pkm("Roselia", "Basic", ["Grass"], 70, [
        _atk("Soothing Scent", ["Grass"], 0, "Your opponent's Active Pokémon is now Asleep."),
    ], weakness="Fire"),
    _pkm("Cubone", "Basic", ["Fighting"], 70, [_atk("Headbutt", ["Fighting"], 30)], weakness="Grass"),
    _pkm("Graveler", "Stage1", ["Fighting"], 110, [_atk("Rollout", ["Fighting"], 40), _atk("Rock Slide", ["Fighting", "Colorless", "Colorless"], 80)], evolves_from="Geodude", weakness="Grass"),
    _pkm("Rockruff", "Basic", ["Fighting"], 60, [
        _atk("Invite Out", ["Colorless"], 0, "Flip a coin. If heads, switch 1 of your opponent's Benched Pokémon with their Active Pokémon."),
        _atk("Smash Kick", ["Fighting", "Colorless"], 20),
    ], weakness="Grass", catalog_id="swsh12.5-073"),
    _pkm("Salazzle", "Stage1", ["Fire"], 120, [
        _atk("Tail Trickery", ["Colorless"], 20, "Your opponent's Active Pokémon is now Confused."),
        _atk("Super Singe", ["Fire", "Colorless"], 60, "Your opponent's Active Pokémon is now Burned."),
    ], evolves_from="Salandit", weakness="Water"),
    _pkm("Combusken", "Stage1", ["Fire"], 90, [_atk("Rolling Fireball", ["Fire", "Colorless"], 60)], evolves_from="Torchic", weakness="Water"),
    _pkm("Crocalor", "Stage1", ["Fire"], 100, [_atk("Rolling Fireball", ["Fire", "Fire"], 90, "Put an Energy attached to this Pokémon into your hand.")], evolves_from="Fuecoco", weakness="Water"),
    _pkm("Bronzor", "Basic", ["Metal"], 70, [_atk("Spinning Attack", ["Colorless"], 10)], retreat=2, catalog_id="swsh11-125", weakness="Fire"),
    _pkm("Metang", "Stage1", ["Metal"], 100, [
        _atk("Bullet Punch", ["Metal", "Colorless"], 30, "Flip 2 coins. This attack does 30 more damage for each heads."),
    ], evolves_from="Beldum", retreat=2, catalog_id="swsh12.5-090", weakness="Fire"),
    _pkm("Orthworm", "Basic", ["Metal"], 140, [
        _atk("Punch and Draw", ["Metal"], 20, "Draw 2 cards."),
        _atk(
            "Crunch-Time Rush",
            ["Metal", "Colorless", "Colorless"],
            90,
            "If there are 3 or fewer cards in your deck, this attack does 150 more damage.",
        ),
    ], retreat=3, catalog_id="sv04-138", weakness="Fire"),
    _pkm("Baltoy", "Basic", ["Fighting"], 60, [_atk("Smack", ["Fighting"], 20)], weakness="Grass", catalog_id="swsh12.5-070"),
    _pkm("Carbink", "Basic", ["Fighting"], 90, [
        _atk(
            "Lucky Find",
            ["Colorless"],
            0,
            "Search your deck for up to 2 Item cards, reveal them, and put them into your hand. Then, shuffle your deck.",
        ),
        _atk("Power Gem", ["Fighting", "Fighting", "Colorless"], 80),
    ], weakness="Grass", catalog_id="swsh11-108"),
    _pkm("Poliwhirl", "Stage1", ["Water"], 90, [
        _atk("Light Punch", ["Colorless", "Colorless"], 30),
        _atk("Double Smash", ["Water", "Colorless", "Colorless"], 50, "Flip 2 coins. This attack does 50 damage for each heads."),
    ], evolves_from="Poliwag", retreat=2, catalog_id="swsh11-031", weakness="Lightning"),
    _pkm("Phantump", "Basic", ["Grass"], 70, [_atk("Hook", ["Colorless"], 10)], retreat=2, catalog_id="swsh11-016", weakness="Fire"),
    _pkm("Gloom", "Stage1", ["Grass"], 80, [
        _atk("Absorb", ["Grass", "Colorless"], 30, "Heal 30 damage from this Pokémon."),
    ], evolves_from="Oddish", retreat=2, catalog_id="swsh11-002", weakness="Fire"),
    _pkm("Oddish", "Basic", ["Grass"], 50, [_atk("Leaf Boomerang", ["Grass"], 10)], weakness="Fire"),
    _pkm("Dusclops", "Stage1", ["Psychic"], 90, [_atk("Fade to Black", ["Psychic"], 30, "Your opponent's Active Pokémon is now Confused.")], evolves_from="Duskull", retreat=2, catalog_id="swsh12.5-063", weakness="Darkness"),
    _pkm("Pumpkaboo", "Basic", ["Psychic"], 60, [
        _atk("Seed Bomb", ["Psychic"], 10),
        _atk("Reckless Charge", ["Colorless", "Colorless"], 40, "This Pokémon also does 20 damage to itself."),
    ], retreat=2, catalog_id="sv04-077", weakness="Darkness"),
    _pkm("Kadabra", "Stage1", ["Psychic"], 80, [_atk("Teleportation Attack", ["Psychic"], 30, "Switch this Pokémon with 1 of your Benched Pokémon.")], evolves_from="Abra", weakness="Darkness"),
    _pkm(
        "Clefairy",
        "Basic",
        ["Psychic"],
        60,
        [
            _atk(
                "Wonder Storm",
                ["Colorless", "Colorless", "Colorless"],
                20,
                "This attack does 20 damage for each Psychic Energy attached to all of your Pokémon.",
            )
        ],
        catalog_id="swsh11-062",
        weakness="Metal",
        retreat=2,
        abilities=[
            Ability(
                name="Moon-Watching Party",
                text=(
                    "Once during your turn, if this Pokémon is in the Active Spot, for each of your Benched "
                    "Clefairy, you may search your deck for a Psychic Energy card and attach it to that "
                    "Clefairy. Then, shuffle your deck."
                ),
            )
        ],
    ),
    _pkm(
        "Clefable",
        "Stage1",
        ["Psychic"],
        110,
        [_atk("Moon Kick", ["Psychic", "Colorless"], 60)],
        evolves_from="Clefairy",
        catalog_id="swsh2-75",
        weakness="Metal",
        retreat=2,
        abilities=[
            Ability(
                name="Prankish",
                text=(
                    "When you play this Pokémon from your hand to evolve 1 of your Pokémon during your turn, "
                    "you may put an Energy attached to your opponent's Active Pokémon on top of their deck."
                ),
            )
        ],
    ),
    _pkm(
        "Clefable ex",
        "Stage1",
        ["Psychic"],
        260,
        [
            _atk(
                "Wondrous Moon",
                ["Psychic", "Psychic", "Psychic"],
                170,
                "You may move any amount of Psychic Energy from your Pokémon to your other Pokémon in any way you like.",
            )
        ],
        evolves_from="Clefairy",
        catalog_id="sv03-082",
        weakness="Metal",
        retreat=2,
        abilities=[
            Ability(
                name="Lunar Zone",
                text="All of your Pokémon that have Psychic Energy attached have no Retreat Cost.",
            )
        ],
    ),
    _pkm(
        "Mega Clefable ex",
        "Stage1",
        ["Psychic"],
        320,
        [
            _atk(
                "Shooting Moons",
                ["Psychic", "Psychic"],
                120,
                "You may discard up to 4 Energy cards from your hand, and this attack does 40 more damage for each card you discarded in this way.",
            )
        ],
        evolves_from="Clefairy",
        catalog_id="me03-031",
        weakness="Metal",
        retreat=1,
        abilities=[
            Ability(
                name="Luminous Wing",
                text="Prevent all effects of your opponent's Pokémon's Abilities done to this Pokémon.",
            )
        ],
    ),
    _pkm(
        "Mewtwo ex",
        "Basic",
        ["Lightning"],
        230,
        [
            _atk(
                "Transfer Charge",
                ["Psychic"],
                0,
                "Attach up to 2 Basic Psychic Energy cards from your discard pile to your Pokémon in any way you like.",
            ),
            _atk(
                "Photon Kinesis",
                ["Psychic", "Psychic"],
                10,
                "This attack does 30 more damage for each Psychic Energy attached to all of your Pokémon.",
            ),
        ],
        catalog_id="sv04-058",
        weakness="Fighting",
        retreat=2,
    ),
    _pkm(
        "Wo-Chien ex",
        "Basic",
        ["Grass"],
        230,
        [
            _atk(
                "Covetous Ivy",
                ["Grass", "Grass", "Colorless"],
                0,
                "This attack does 60 damage to 1 of your opponent's Benched Pokémon for each Prize card your opponent has taken. (Don't apply Weakness and Resistance for Benched Pokémon.)",
            ),
            _atk(
                "Forest Blast",
                ["Grass", "Grass", "Grass", "Colorless"],
                220,
            ),
        ],
        catalog_id="sv02-027",
        weakness="Fire",
        retreat=4,
        image="https://assets.tcgdex.net/en/sv/sv02/027/low.webp",
        set_name="Paldea Evolved",
    ),
    _pkm(
        "Cornerstone Mask Ogerpon ex",
        "Basic",
        ["Fighting"],
        210,
        [
            _atk(
                "Demolish",
                ["Fighting", "Colorless", "Colorless"],
                140,
                "This attack's damage isn't affected by Weakness or Resistance, or by any effects on your opponent's Active Pokémon.",
            )
        ],
        catalog_id="sv06-112",
        weakness="Grass",
        retreat=1,
        abilities=[
            Ability(
                name="Cornerstone Stance",
                text="Prevent all damage from attacks done to this Pokémon by your opponent's Pokémon that have an Ability.",
            )
        ],
    ),
    _pkm(
        "Mr. Mime",
        "Basic",
        ["Psychic"],
        40,
        [
            _atk(
                "Meditate",
                ["Psychic", "Colorless"],
                10,
                "Does 10 damage plus 10 more damage for each damage counter on the Defending Pokémon.",
            )
        ],
        catalog_id="base2-6",
        weakness="Psychic",
        retreat=1,
        abilities=[
            Ability(
                name="Invisible Wall",
                text=(
                    "Whenever an attack (including your own) does 30 or more damage to Mr. Mime "
                    "(after applying Weakness and Resistance), prevent that damage. "
                    "(Any other effects of attacks still happen.) This power can't be used if "
                    "Mr. Mime is Asleep, Confused, or Paralyzed."
                ),
            )
        ],
    ),
    _pkm(
        "Flutter Mane",
        "Basic",
        ["Psychic"],
        90,
        [
            _atk(
                "Hex Hurl",
                ["Colorless", "Colorless", "Colorless"],
                90,
                "Put 2 damage counters on your opponent's Benched Pokémon in any way you like.",
            )
        ],
        catalog_id="sv05-078",
        weakness="Metal",
    ),
    _pkm("Hisuian Sliggoo", "Stage1", ["Dragon"], 90, [_atk("Rigidify", ["Colorless"], 0), _atk("Gentle Slap", ["Water", "Metal"], 40)], evolves_from="Goomy", weakness="Dragon"),
    _pkm("Sudowoodo", "Basic", ["Fighting"], 110, [
        _atk("Joust", ["Fighting"], 20),
        _atk("Impound", ["Fighting", "Colorless"], 50, "During your opponent's next turn, the Defending Pokémon can't retreat."),
    ], weakness="Water", catalog_id="swsh11-094"),
    _pkm("Gible", "Basic", ["Fighting"], 70, [_atk("Bite", ["Fighting"], 20)], weakness="Grass", catalog_id="sv04-094"),
    _pkm("Relicanth", "Basic", ["Fighting"], 90, [_atk("Into the Deep", ["Colorless"], 0), _atk("Tackle", ["Fighting", "Colorless"], 80)], weakness="Grass"),
    _pkm("Tangela", "Basic", ["Grass"], 80, [
        _atk("Beat", ["Colorless"], 10),
        _atk("Vine Whip", ["Grass", "Grass", "Colorless"], 60),
    ], retreat=2, weakness="Fire", catalog_id="swsh12.5-004"),
    _pkm(
        "Gimmighoul",
        "Basic",
        ["Psychic"],
        50,
        [
            _atk(
                "Call for Family",
                ["Colorless"],
                0,
                "Search your deck for a Basic Pokémon and put it onto your Bench. Then, shuffle your deck.",
            ),
            _atk("Corkscrew Punch", ["Colorless", "Colorless"], 20),
        ],
        weakness="Darkness",
        catalog_id="sv04-087",
    ),
    _pkm("Plusle", "Basic", ["Lightning"], 70, [_atk(
        "Plus Damage",
        ["Colorless", "Colorless"],
        10,
        "This attack does 10 more damage for each damage counter on your opponent's Active Pokémon.",
    )], weakness="Fighting"),
    _pkm("Lickilicky", "Stage1", ["Colorless"], 140, [_atk("Tongue Slap", ["Colorless"], 40), _atk("Heavy Impact", ["Colorless", "Colorless", "Colorless"], 90)], evolves_from="Lickitung", weakness="Fighting"),
    _pkm("Slugma", "Basic", ["Fire"], 70, [
        _atk("Draw In", ["Fire"], 0, "Attach a Fire Energy card from your discard pile to this Pokémon."),
        _atk("Combustion", ["Fire", "Fire", "Colorless"], 50),
    ], retreat=2, weakness="Water", catalog_id="swsh11-021"),
    _pkm(
        "Litwick",
        "Basic",
        ["Fire"],
        60,
        [
            _atk(
                "Kindling Panic",
                ["Fire"],
                0,
                "Discard the top card of your opponent's deck.",
            )
        ],
        weakness="Water",
        catalog_id="swsh11-024",
    ),
    _pkm("Ferroseed", "Basic", ["Metal"], 70, [_atk("Spike Sting", ["Metal", "Colorless"], 30)], retreat=2, weakness="Fire", catalog_id="sv04-127"),
    _pkm("Galarian Meowth", "Basic", ["Metal"], 70, [
        _atk("Fasten Claws", ["Metal"], 10, "Flip a coin. If heads, this attack does 20 more damage."),
    ], weakness="Fire", catalog_id="swsh12.5-084"),
    _pkm("Aron", "Basic", ["Metal"], 70, [
        _atk("Ram", ["Metal"], 10),
        _atk("Slight Intrusion", ["Colorless", "Colorless"], 30, "This Pokémon also does 10 damage to itself."),
    ], retreat=2, weakness="Fire", catalog_id="swsh12.5-087"),
    _pkm("Electrike", "Basic", ["Lightning"], 60, [
        _atk("Zap Kick", ["Lightning"], 10),
        _atk("Thunder Fang", ["Colorless", "Colorless"], 20, "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed."),
    ], weakness="Fighting", catalog_id="swsh11-054"),
    _pkm("Pichu", "Basic", ["Lightning"], 30, [_atk("Mix-Up", ["Colorless"], 0, "Draw a card.")], weakness="Fighting"),
    _pkm(
        "Emolga",
        "Basic",
        ["Lightning"],
        70,
        [
            _atk(
                "Call for Family",
                ["Colorless"],
                0,
                "Search your deck for up to 2 Basic Pokémon and put them onto your Bench. Then, shuffle your deck.",
            ),
            _atk("Static Shock", ["Lightning"], 40),
        ],
        weakness="Fighting",
        catalog_id="sv10.5b-029",
    ),
    _pkm("Dedenne", "Basic", ["Psychic"], 70, [_atk("Call for Family", ["Colorless"], 0, "Search your deck for a Basic Pokémon."), _atk("Voltish Pulse", ["Psychic"], 30, "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed.")], weakness="Metal"),
    _pkm(
        "Gligar",
        "Basic",
        ["Fighting"],
        70,
        [
            _atk(
                "Toxic",
                ["Colorless"],
                0,
                "Flip a coin. If heads, your opponent's Active Pokémon is now Poisoned. During Pokémon Checkup, put 2 damage counters on that Pokémon instead of 1.",
            )
        ],
        weakness="Grass",
        catalog_id="sv04-091",
    ),
    _pkm(
        "Starly",
        "Basic",
        ["Colorless"],
        60,
        [_atk("Flap", ["Colorless"], 20)],
        weakness="Lightning",
        catalog_id="sv01-148",
    ),
    _pkm(
        "Staravia",
        "Stage1",
        ["Colorless"],
        80,
        [
            _atk("Wing Attack", ["Colorless", "Colorless"], 40),
            _atk("Speed Dive", ["Colorless", "Colorless", "Colorless"], 80),
        ],
        evolves_from="Starly",
        weakness="Lightning",
        catalog_id="sv01-149",
    ),
    _pkm(
        "Staraptor",
        "Stage2",
        ["Colorless"],
        150,
        [
            _atk(
                "Tailspin Away",
                ["Colorless", "Colorless"],
                60,
                "During your opponent's next turn, prevent all damage done to this Pokémon by attacks from Basic Pokémon.",
            ),
            _atk(
                "Power Blast",
                ["Colorless", "Colorless", "Colorless"],
                180,
                "Discard an Energy from this Pokémon.",
            ),
        ],
        evolves_from="Staravia",
        weakness="Lightning",
        catalog_id="sv01-150",
    ),
    _pkm("Aipom", "Basic", ["Colorless"], 60, [
        _atk("Mischievous Tail", ["Colorless"], 0, "Look at the top card of your opponent's deck. You may have your opponent shuffle their deck."),
        _atk("Scratch", ["Colorless", "Colorless"], 10),
    ], weakness="Fighting", catalog_id="swsh11-144"),
    _pkm(
        "Spheal",
        "Basic",
        ["Water"],
        70,
        [_atk("Powder Snow", ["Water"], 10, "Your opponent's Active Pokémon is now Asleep.")],
        retreat=2,
        weakness="Metal",
        catalog_id="sv08-043",
    ),
    _pkm(
        "Sealeo",
        "Stage1",
        ["Water"],
        100,
        [_atk("Lunge Out", ["Water"], 30), _atk("Ice Ball", ["Water", "Water"], 60)],
        evolves_from="Spheal",
        retreat=3,
        weakness="Metal",
        catalog_id="sv08-044",
    ),
    _pkm(
        "Walrein",
        "Stage2",
        ["Water"],
        170,
        [
            _atk(
                "Frigid Fangs",
                ["Water"],
                60,
                "During your opponent's next turn, Pokémon that have 2 or less Energy attached can't attack. (This includes new Pokémon that come into play.)",
            ),
            _atk(
                "Megaton Fall",
                ["Water", "Water"],
                170,
                "This Pokémon also does 50 damage to itself.",
            ),
        ],
        evolves_from="Sealeo",
        retreat=3,
        weakness="Metal",
        catalog_id="sv08-045",
    ),
    _pkm("Corphish", "Basic", ["Water"], 70, [
        _atk("Water Gun", ["Colorless"], 10),
        _atk("Crabhammer", ["Water", "Colorless", "Colorless"], 50),
    ], retreat=2, catalog_id="swsh12.5-033", weakness="Lightning"),
    _pkm("Wailmer", "Basic", ["Water"], 120, [
        _atk("Nap", ["Colorless"], 0, "Heal 30 damage from this Pokémon."),
        _atk("Water Gun", ["Colorless", "Colorless", "Colorless"], 70),
    ], weakness="Lightning", catalog_id="swsh12.5-031"),
    _pkm("Spinarak", "Basic", ["Darkness"], 50, [_atk("Poison Sting", ["Darkness"], 10, "Your opponent's Active Pokémon is now Poisoned.")], weakness="Fighting", catalog_id="swsh11-112"),
    _pkm("Lickitung", "Basic", ["Colorless"], 90, [_atk("Tongue Slap", ["Colorless"], 30), _atk("Heavy Impact", ["Colorless", "Colorless"], 50)], weakness="Fighting"),
    _pkm(
        "Dreepy",
        "Basic",
        ["Dragon"],
        70,
        [
            _atk("Petty Grudge", ["Psychic"], 10),
            _atk("Bite", ["Fire", "Psychic"], 40),
        ],
        weakness=None,
        catalog_id="sv06-128",
        image="https://assets.tcgdex.net/en/sv/sv06/128/low.webp",
        set_name="Twilight Masquerade",
    ),
    _pkm(
        "Drakloak",
        "Stage1",
        ["Dragon"],
        90,
        [_atk("Dragon Headbutt", ["Fire", "Psychic"], 70)],
        evolves_from="Dreepy",
        abilities=[
            Ability(
                name="Recon Directive",
                text=(
                    "Once during your turn, you may look at the top 2 cards of your "
                    "deck and put 1 of them into your hand. Put the other card on "
                    "the bottom of your deck."
                ),
            )
        ],
        weakness=None,
        catalog_id="sv06-129",
        image="https://assets.tcgdex.net/en/sv/sv06/129/low.webp",
        set_name="Twilight Masquerade",
    ),
    _pkm(
        "Dragapult ex",
        "Stage2",
        ["Dragon"],
        320,
        [
            _atk("Jet Headbutt", ["Colorless"], 70),
            _atk(
                "Phantom Dive",
                ["Fire", "Psychic"],
                200,
                "Put 6 damage counters on your opponent's Benched Pokémon in any way you like.",
            ),
        ],
        evolves_from="Drakloak",
        weakness=None,
        catalog_id="sv06-130",
        image="https://assets.tcgdex.net/en/sv/sv06/130/low.webp",
        set_name="Twilight Masquerade",
    ),
    _pkm(
        "Fezandipiti ex",
        "Basic",
        ["Darkness"],
        210,
        [
            _atk(
                "Cruel Arrow",
                ["Colorless", "Colorless", "Colorless"],
                0,
                "This attack does 100 damage to 1 of your opponent's Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)",
            )
        ],
        abilities=[
            Ability(
                name="Flip the Script",
                text=(
                    "Once during your turn, if any of your Pokémon were Knocked Out "
                    "during your opponent's last turn, you may draw 3 cards. You can't "
                    "use more than 1 Flip the Script Ability each turn."
                ),
            )
        ],
        weakness="Fighting",
        catalog_id="sv06.5-038",
        image="https://assets.tcgdex.net/en/sv/sv06.5/038/low.webp",
        set_name="Shrouded Fable",
    ),
    _pkm(
        "Budew",
        "Basic",
        ["Grass"],
        30,
        [
            _atk(
                "Itchy Pollen",
                [],
                10,
                "During your opponent's next turn, they can't play any Item cards from their hand.",
            )
        ],
        retreat=0,
        weakness="Fire",
        catalog_id="sv08.5-004",
        image="https://assets.tcgdex.net/en/sv/sv08.5/004/low.webp",
        set_name="Prismatic Evolutions",
    ),
]:
    _register(card)

# TWM / CLC Clefable keep the printed name "Clefable" but live under alias keys so they
# do not overwrite Rebel Clash Prankish in FALLBACK_BY_NAME.
_CLEFABLE_TWM = _pkm(
    "Clefable",
    "Stage1",
    ["Psychic"],
    120,
    [
        _atk(
            "Metronome",
            ["Colorless", "Colorless"],
            0,
            "Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack.",
        ),
        _atk("Magical Shot", ["Psychic", "Colorless", "Colorless"], 100),
    ],
    evolves_from="Clefairy",
    catalog_id="sv06-079",
    weakness="Metal",
    retreat=2,
    image="https://assets.tcgdex.net/en/sv/sv06/079/low.webp",
    set_name="Twilight Masquerade",
)
_CLEFABLE_CLC = _pkm(
    "Clefable",
    "Stage1",
    ["Colorless"],
    70,
    [
        _atk(
            "Metronome",
            ["Colorless"],
            0,
            "Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack.",
        ),
        _atk(
            "Minimize",
            ["Colorless", "Colorless"],
            0,
            "During your opponent's next turn, this Pokémon takes 20 less damage from attacks (after applying Weakness and Resistance).",
        ),
    ],
    evolves_from="Clefairy",
    catalog_id="clc-014",
    weakness="Fighting",
    retreat=2,
    resistances=[{"type": "Psychic", "value": "-30"}],
    set_name="Pokémon TCG Classic",
)
FALLBACK_BY_NAME["clefable twm"] = _CLEFABLE_TWM
FALLBACK_BY_NAME["clefable (twilight masquerade)"] = _CLEFABLE_TWM
FALLBACK_BY_NAME["clefable clc"] = _CLEFABLE_CLC
FALLBACK_BY_NAME["clefable (clc 014)"] = _CLEFABLE_CLC
FALLBACK_BY_NAME["clefable cmc 014"] = _CLEFABLE_CLC

# Set B carpet Pikachu: Tail Whap / Thunder Shock.
_register(_pkm(
    "Pikachu",
    "Basic",
    ["Lightning"],
    60,
    [
        _atk("Tail Whap", ["Colorless"], 10),
        _atk(
            "Thunder Shock",
            ["Lightning", "Colorless"],
            20,
            "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed.",
        ),
    ],
    catalog_id="sm3-40",
    weakness="Fighting",
))

# Set A carpet Pikachu (traded to B): Nuzzle / Volt Tackle.
FALLBACK_BY_NAME["pikachu-nuzzle"] = _pkm(
    "Pikachu",
    "Basic",
    ["Lightning"],
    60,
    [
        _atk(
            "Nuzzle",
            ["Lightning"],
            0,
            "Flip a coin. If heads, your opponent's Active Pokémon is now Paralyzed.",
        ),
        _atk(
            "Volt Tackle",
            ["Lightning", "Lightning", "Colorless"],
            70,
            "This Pokémon does 10 damage to itself.",
        ),
    ],
    catalog_id="sm12-66",
    weakness="Fighting",
)


def fallback_named(name: str) -> Card:
    key = name.lower()
    if "double colorless" in key:
        key = "double colorless energy"
    if "boomerang" in key:
        key = "boomerang energy"
    if key in FALLBACK_BY_NAME:
        card = FALLBACK_BY_NAME[key]
        return Card.from_dict(card.to_dict())
    if key.endswith(" energy") and "double" not in key:
        return _nrg(name.split()[0].title())
    from app.catalog import fallback_card

    return fallback_card(name)


def build_fallback_deck(names: list[str]) -> list[Card]:
    return [fallback_named(n) for n in names]
