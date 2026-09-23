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

# Set C — Clefairy / Mewtwo vs Charm Ogerpon. 30: 4 Rebel Clash Clefable (name cap) + 4th Mega
# + Boss's Orders. No dedicated Energy; Rule B treats the line as Psychic. Clefable / Clefable ex /
# Mega Clefable ex are different names (4 each). TWM/CLC share the Clefable name. Maximum Belt is ACE SPEC.
# Tool Box tutors it from the top 7; Arven is the full-deck Tool + Item search.
# Moon-Watching Party is LOR 62 full-deck search. 2 Hop + 1 SM Lillie (UPR first-turn 8).
SET_C_NAMES = (
    ["Clefairy"] * 4
    + ["Mewtwo ex"] * 2
    + ["Clefable"] * 4
    + ["Clefable ex"] * 4
    + ["Mega Clefable ex"] * 4
    + ["Hop"] * 2
    + ["Lillie"]
    + ["Nest Ball"] * 2
    + ["Energy Search"] * 3
    + ["Maximum Belt"]
    + ["Tool Box"]
    + ["Arven"]
    + ["Boss's Orders"]
)

# Set C → Standard 60 (preset s60). Pokémon are not energy, so the 30-card
# Clefable pile is thinned and 14 Psychic Energy + 2 Telepathic Psychic Energy
# pay Party / Photon / Zone. Telepathic attaches from hand onto a Psychic
# Pokémon, then benches up to 2 Basic Psychic; Party cannot search it from the deck.
# Arven still tutors Maximum Belt; Tool Box (top 7) lost the 1-for-1 to a 14th Psychic.
# Keep LOR 62 Clefairy as the engine; add Switch so Party can fire from Active;
# Poffin benches 60 HP Clefairy; more Boss for a 6-prize race.
# 3 Battle Cage (both benches ignore opp counter placement; damage still taken)
# for -Jacq -Energy Retrieval -1 Iono: T60 51.3 -> 69.1, Hedrick 59.0 -> 64.6,
# UNL 82.8 -> 89.5, D60 holds 76.1. Rabsca 1-1 does nothing (+0-1, fragile 1-1);
# Shaymin blocks damage only, not Dive counters. See set-c60-bench-shield.md.
# Bounce-slot matrix (2026-09-22, seed 20260922, 3,000/cell): Penny, Turo,
# Briney, Seeker, AZ, and Cheren's Care in these five slots all lose to this
# list. The live 2/1/1/1 package, with Seeker's one-bench KO line, is T60 58.3 /
# D60 62.2 against this list's 68.8 / 75.8. See data/lab/set-c60-bounce-combo.md.
# The cards stay in the engine; they are not in the 60.
# Frozen cage 60 (2 Rebel Clash Prankish, 2 Mega, 0 Pad) for historical bakeoffs.
C60_CAGE_LOCK_NAMES = (
    ["Clefairy"] * 4
    + ["Mewtwo ex"] * 3
    + ["Clefable"] * 2
    + ["Clefable ex"] * 3
    + ["Mega Clefable ex"] * 2
    + ["Nest Ball"] * 4
    + ["Buddy-Buddy Poffin"] * 4
    + ["Ultra Ball"] * 2
    + ["Hop"] * 2
    + ["Lillie"] * 2
    + ["Lillie's Determination"] * 2
    + ["Arven"]
    + ["Boss's Orders"] * 3
    + ["Iono"]
    + ["Switch"] * 2
    + ["Energy Switch"] * 2
    + ["Night Stretcher"]
    + ["Maximum Belt"]
    + ["Battle Cage"] * 3
    + ["Telepathic Psychic Energy"] * 2
    + ["Psychic Energy"] * 14
)

# Live lock (2026-09-22, seed 20260922): 1 Rebel Clash Prankish + 1 CLC 014
# Metronome + 1 Poké Pad (ME02.5 198, no Rule Box), paid by cutting the second
# Prankish and the second Mega. Cut matrix wComp: mega 69.6, pad-only 69.3,
# 2-Prankish 68.5. See data/lab/set-c60-pad-clc-cuts.md.
SET_C60_NAMES = (
    ["Clefairy"] * 4
    + ["Mewtwo ex"] * 3
    + ["Clefable"]
    + ["Clefable CLC"]
    + ["Clefable ex"] * 3
    + ["Mega Clefable ex"]
    + ["Nest Ball"] * 4
    + ["Buddy-Buddy Poffin"] * 4
    + ["Ultra Ball"] * 2
    + ["Hop"] * 2
    + ["Lillie"] * 2
    + ["Lillie's Determination"] * 2
    + ["Arven"]
    + ["Boss's Orders"] * 3
    + ["Iono"]
    + ["Switch"] * 2
    + ["Energy Switch"] * 2
    + ["Night Stretcher"]
    + ["Maximum Belt"]
    + ["Battle Cage"] * 3
    + ["Telepathic Psychic Energy"] * 2
    + ["Psychic Energy"] * 14
    + ["Poké Pad"]
)


def c60_names_before_bounce() -> list[str]:
    """Cage-lock C60 (2 Prankish, 2 Mega, 0 Pad). Frozen for historical bakeoffs."""
    return list(C60_CAGE_LOCK_NAMES)

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

# Set D / S / T stretched to Standard 60 for s60 bakeoffs (Pokémon are not energy).
SET_D60_NAMES = (
    ["Cornerstone Mask Ogerpon ex"] * 4
    + ["Nest Ball"] * 4
    + ["Energy Search"] * 4
    + ["Ultra Ball"] * 4
    + ["Switch"] * 4
    + ["Bravery Charm"] * 4
    + ["Boss's Orders"] * 4
    + ["Iono"] * 4
    + ["Acerola"] * 2
    + ["Hop"] * 2
    + ["Lillie"] * 2
    + ["Night Stretcher"] * 2
    + ["Energy Retrieval"] * 2
    + ["Fighting Energy"] * 14
    + ["Double Colorless Energy"] * 4
)

SET_S60_NAMES = (
    ["Sprigatito"] * 4
    + ["Floragato"] * 4
    + ["Wo-Chien ex"] * 3
    + ["Tangela"] * 2
    + ["Nest Ball"] * 4
    + ["Energy Search"] * 4
    + ["Switch"] * 4
    + ["Ultra Ball"] * 4
    + ["Iono"] * 4
    + ["Boss's Orders"] * 2
    + ["Hop"] * 2
    + ["Night Stretcher"] * 2
    + ["Jacq"]
    + ["Maximum Belt"]
    + ["Tool Box"]
    + ["Arven"]
    + ["Grass Energy"] * 17
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

SET_T60_NAMES = (
    ["Dreepy"] * 4
    + ["Drakloak"] * 3
    + ["Dragapult ex"] * 3
    + ["Fezandipiti ex"] * 2
    + ["Budew"] * 2
    + ["Buddy-Buddy Poffin"] * 4
    + ["Ultra Ball"] * 4
    + ["Rare Candy"] * 4
    + ["Lillie's Determination"] * 4
    + ["Boss's Orders"] * 4
    + ["Iono"] * 2
    + ["Judge"] * 2
    + ["Crispin"] * 2
    + ["Night Stretcher"] * 2
    + ["Poké Pad"] * 2
    + ["Crushing Hammer"] * 2
    + ["Nest Ball"]
    + ["Energy Search"]
    + ["Unfair Stamp"]
    + ["Fire Energy"] * 5
    + ["Psychic Energy"] * 4
    + ["Darkness Energy"] * 2
)

# Worlds 2026 Andrew Hedrick Dragapult (Limitless #28752). Printed 60.
SET_T_META_NAMES = (
    ["Dreepy"] * 4
    + ["Drakloak"] * 4
    + ["Dragapult ex"] * 3
    + ["Munkidori"] * 2
    + ["Budew"] * 2
    + ["Dunsparce"]
    + ["Dudunsparce"]
    + ["Meowth ex"]
    + ["Fezandipiti ex"]
    + ["Lillie's Determination"] * 4
    + ["Boss's Orders"] * 3
    + ["Crispin"] * 2
    + ["Rosa's Encouragement"]
    + ["Poké Pad"] * 4
    + ["Crushing Hammer"] * 4
    + ["Buddy-Buddy Poffin"] * 4
    + ["Night Stretcher"] * 3
    + ["Ultra Ball"] * 3
    + ["Unfair Stamp"]
    + ["Special Red Card"]
    + ["Risky Ruins"] * 2
    + ["Fire Energy"] * 3
    + ["Darkness Energy"] * 3
    + ["Psychic Energy"] * 3
)

# Unlimited Dragapult extras (Pidgeot / Rotom V / Counter Catcher package). Printed 60.
SET_T_UNL_NAMES = (
    ["Dreepy"] * 4
    + ["Drakloak"] * 2
    + ["Dragapult ex"] * 3
    + ["Pidgey"] * 2
    + ["Pidgeotto"]
    + ["Pidgeot ex"] * 2
    + ["Rotom V"]
    + ["Fezandipiti ex"]
    + ["Lumineon V"]
    + ["Manaphy"]
    + ["Arven"] * 4
    + ["Iono"] * 4
    + ["Boss's Orders"] * 2
    + ["Crispin"]
    + ["Nest Ball"] * 4
    + ["Buddy-Buddy Poffin"] * 4
    + ["Rare Candy"] * 4
    + ["Ultra Ball"] * 4
    + ["Counter Catcher"] * 2
    + ["Night Stretcher"]
    + ["Earthen Vessel"]
    + ["Switch"]
    + ["Forest Seal Stone"]
    + ["Super Rod"]
    + ["Professor Turo's Scenario"]
    + ["Collapsed Stadium"]
    + ["Fire Energy"] * 3
    + ["Psychic Energy"] * 3
)

# Set M Standard 60: Zero-Energy Mew ex & Igglybuff Baby Box (Optimized Option C: 4 Mew ex, 4 Igglybuff, 4 Charm, 1 Switch).
SET_M60_NAMES = (
    ["Mew ex"] * 4
    + ["Mime Jr."] * 2
    + ["Igglybuff"] * 4
    + ["Budew"] * 3
    + ["Cleffa"] * 2
    + ["Buddy-Buddy Poffin"] * 4
    + ["Nest Ball"] * 4
    + ["Ultra Ball"] * 4
    + ["Night Stretcher"] * 4
    + ["Battle Cage"] * 4
    + ["Bravery Charm"] * 4
    + ["Maximum Belt"]
    + ["Arven"] * 4
    + ["Iono"] * 4
    + ["Professor's Research"] * 2
    + ["Boss's Orders"] * 3
    + ["Crushing Hammer"] * 4
    + ["Switch"] * 1
    + ["Counter Catcher"] * 2
)
SET_M_NAMES = SET_M60_NAMES
SET_MEW_BABY_60_NAMES = SET_M60_NAMES

# Unlimited 60: Ambipom PAR Hand Fling, Lopunny FLF Big Jump recycle,
# Raikou V Fleet-Footed + Forest Seal Stone Star Alchemy, Draw Energy, Rare Candy.
# 4/4 Aipom–Ambipom is the 2-for-1 prize race (100 HP / 1 prize vs household 2-prizers).
SET_G30_NAMES = (
    ["Buneary"] * 3
    + ["Lopunny"] * 2
    + ["Porygon"] * 3
    + ["Porygon-Z"] * 2
    + ["Aipom"] * 4
    + ["Ambipom"] * 4
    + ["Raikou V"]
    + ["Puzzle of Time"] * 4
    + ["Scoop Up Net"] * 2
    + ["Broken Time-Space"] * 3
    + ["Nest Ball"]
    + ["Buddy-Buddy Poffin"] * 3
    + ["Ultra Ball"] * 3
    + ["VS Seeker"] * 3
    + ["Wally"] * 2
    + ["Professor's Research"]
    + ["Battle Compressor"]
    + ["Switch"]
    + ["Rare Candy"] * 4
    + ["Forest Seal Stone"]
    + ["Enriching Energy"]
    + ["Speed Lightning Energy"] * 4
    + ["Lightning Energy"] * 3
    + ["Draw Energy"] * 4
)

# Carpet Set E — new beige-carpet photo (data/samples/set-e-carpet.jpg).
# Dual Pikachu + Surging Sparks Spheal line. Trainers: Surfer + Iris's Fighting Spirit.
SET_E_NAMES = [
    "Trekking Shoes",
    "Energy Search",
    "Energy Retrieval",
    "Surfer",
    "Lake Acuity",
    "Iris's Fighting Spirit",
    "Pikachu",
    "Pikachu",
    "Emolga",
    "Plusle",
    "Electrike",
    "Lightning Energy",
    "Lightning Energy",
    "Lightning Energy",
    "Lightning Energy",
    "Spheal",
    "Sealeo",
    "Walrein",
    "Wailmer",
    "Water Energy",
    "Water Energy",
    "Water Energy",
    "Water Energy",
    "Water Energy",
    "Sudowoodo",
    "Hippopotas",
    "Gengar",
    "Fighting Energy",
    "Fighting Energy",
    "Fighting Energy",
]

# Carpet Set F — second beige-carpet photo (data/samples/set-f-carpet.jpg).
# Staraptor line + ghost line; dedicated Water / Psychic / Metal Energy (no Pokémon-as-energy).
SET_F_NAMES = [
    "Iono",
    "Ultra Ball",
    "Nest Ball",
    "Switch Cart",
    "Energy Search",
    "Wailmer",
    "Water Energy",
    "Water Energy",
    "Water Energy",
    "Gastly",
    "Haunter",
    "Haunter",
    "Gengar",
    "Scream Tail",
    "Psychic Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Orthworm",
    "Metal Energy",
    "Metal Energy",
    "Metal Energy",
    "Starly",
    "Starly",
    "Staravia",
    "Staraptor",
    "Staraptor",
    "Skwovet",
]

# Carpet Set G — Friday lock (historical). Base for the boss-friday and poffin
# labs. Clefairy is still LOR 62. Mega Clefable ex evolves from Clefairy (was
# Emolga); Tornadus was Mewtwo. Three Boss's Orders replace Potion / Poké Ball
# / Plusle. Indeedee, Relicanth, Hop's Cramorant, Kecleon, Iris's Fighting
# Spirit, Energy Retrieval, Trekking Shoes stay.
SET_G_FRIDAY_NAMES = (
    ["Clefairy"] * 4
    + ["Ledyba"] * 4
    + ["Ledian"] * 4
    + ["Starly"] * 2
    + ["Staravia"] * 2
    + ["Staraptor"] * 2
    + ["Munkidori"] * 2
    + ["Tornadus"]
    + ["Flutter Mane"]
    + ["Indeedee"]
    + ["Relicanth"]
    + ["Mega Clefable ex"]
    + ["Hop's Cramorant"]
    + ["Kecleon"]
    + ["Tulip"]
    + ["Surfer"]
    + ["Drayton"]
    + ["Iris's Fighting Spirit"]
    + ["Energy Retrieval"]
    + ["Trekking Shoes"]
    + ["Energy Search"]
    + ["Energy Switch"]
    + ["Ultra Ball"]
    + ["Boss's Orders"] * 3
    + ["Psychic Energy"] * 17
    + ["Darkness Energy"] * 3
    + ["Boomerang Energy"]
)

# Carpet Set G — Poffin lock. Friday list minus Tornadus / Hop's Cramorant /
# Relicanth / Indeedee, plus the 4 Buddy-Buddy Poffin playset (C60 staple).
# Keeps Kecleon as the 11th Poffin target, the bird line, 4/4 Ledian,
# 3 Darkness, 17 Psychic, Mega, Ultra Ball, Energy Switch, all 4 supporters.
# Frozen so the poffin lab stays reproducible after later arrivals.
# See data/lab/set-g-poffin-c60.md.
SET_G_POFFIN_NAMES = (
    ["Clefairy"] * 4
    + ["Ledyba"] * 4
    + ["Ledian"] * 4
    + ["Starly"] * 2
    + ["Staravia"] * 2
    + ["Staraptor"] * 2
    + ["Munkidori"] * 2
    + ["Flutter Mane"]
    + ["Mega Clefable ex"]
    + ["Kecleon"]
    + ["Tulip"]
    + ["Surfer"]
    + ["Drayton"]
    + ["Iris's Fighting Spirit"]
    + ["Energy Retrieval"]
    + ["Trekking Shoes"]
    + ["Energy Search"]
    + ["Energy Switch"]
    + ["Ultra Ball"]
    + ["Buddy-Buddy Poffin"] * 4
    + ["Boss's Orders"] * 3
    + ["Psychic Energy"] * 17
    + ["Darkness Energy"] * 3
    + ["Boomerang Energy"]
)
# Carpet Set G — Nest / Zone lock. Poffin list minus one Starly, one Staravia,
# one Staraptor, Surfer, Kecleon, Boomerang Energy, Flutter Mane, Energy Search,
# Trekking Shoes, and Tulip. In: 4 Nest Ball, 3 Clefable ex, a second Energy
# Switch, 2 Switch. Bird line stays 1-1-1; Ledian stays 4/4.
# Confirm 3000 games, seed 20260921: t60 20.9→23.9, Hedrick 29.8→34.6,
# D60 5.6→5.4, UNL 44.5→49.3, C60 21.7→22.2, S60 69.8→74.8, H 95.8→96.4.
# Frozen so later Telepathic arrivals stay reproducible.
# See data/lab/set-g-nest-zone.md.
SET_G_NEST_ZONE_NAMES = (
    ["Clefairy"] * 4
    + ["Ledyba"] * 4
    + ["Ledian"] * 4
    + ["Starly"]
    + ["Staravia"]
    + ["Staraptor"]
    + ["Munkidori"] * 2
    + ["Mega Clefable ex"]
    + ["Clefable ex"] * 3
    + ["Drayton"]
    + ["Iris's Fighting Spirit"]
    + ["Energy Retrieval"]
    + ["Energy Switch"] * 2
    + ["Ultra Ball"]
    + ["Nest Ball"] * 4
    + ["Switch"] * 2
    + ["Buddy-Buddy Poffin"] * 4
    + ["Boss's Orders"] * 3
    + ["Psychic Energy"] * 17
    + ["Darkness Energy"] * 3
)


def _replace_n(names: tuple[str, ...], old: str, new: str, n: int) -> tuple[str, ...]:
    out = list(names)
    for _ in range(n):
        out[out.index(old)] = new
    return tuple(out)


# Carpet Set G — Telepathic lock, then one Ledian for a 16th Psychic.
# Nest/Zone minus 2 Psychic plus 2 Telepathic (copies 3 and 4 lose; see
# data/lab/set-g-c60-telepathic.md). Arrival matrix 2026-09-23: Ledian →
# Psychic beat Ledian → Poké Pad on Hedrick, UNL, the C60 mirror, and the
# whole field. T60 −0.6 is inside noise. See data/lab/set-g-c60-arrival.md.
SET_G_NAMES = _replace_n(
    _replace_n(SET_G_NEST_ZONE_NAMES, "Psychic Energy", "Telepathic Psychic Energy", 2),
    "Ledian",
    "Psychic Energy",
    1,
)

# Carpet Set H — 60-card beige-carpet photo (data/samples/set-h-carpet.jpg), Standard s60.
# Destined Rivals Team Rocket's Zapdos (not Roaring Skies Zapdos). Two Pikachu prints.
# One Paradox Rift Zekrom (Hidden Fates sm3.5-35 has no TCGDex art). Photo extras were
# Plusle / Ledyba-Ledian / Minun / Kecleon / Zoroark, not Helioptile / Grookey / Tynamo.
# Six TR Zapdos on the carpet; 4-of keeps four. Energy fills the rest to 60.
SET_H_NAMES = (
    ["Team Rocket's Zapdos"] * 4
    + ["Pikachu"] * 2
    + ["Zekrom"]
    + ["Wattrel"]
    + ["Raichu"]
    + ["Jolteon"]
    + ["Emolga"]
    + ["Shinx"]
    + ["Electrike"]
    + ["Pawmi"]
    + ["Rotom"]
    + ["Plusle"] * 2
    + ["Ledyba"]
    + ["Ledian"]
    + ["Minun"]
    + ["Kecleon"]
    + ["Zoroark"] * 3
    + ["Hisuian Voltorb"]
    + ["Drifblim"]
    + ["Sandygast"]
    + ["Skiddo"]
    + ["Lechonk"]
    + ["Oranguru"]
    + ["Surfer"]
    + ["Iris's Fighting Spirit"]
    + ["Energy Retrieval"]
    + ["Nest Ball"]
    + ["Double Colorless Energy"]
    + ["Lightning Energy"] * 25
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
    from app.catalog import _looks_like_tcgdex_id, _tcgdex_low

    cid = catalog_id or name.lower().replace(" ", "-")
    art = image
    if not art and _looks_like_tcgdex_id(str(cid or "")):
        try:
            art = _tcgdex_low(cid)
        except Exception:
            art = None
    return Card(
        catalog_id=cid,
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
        image=art,
        set_name=set_name,
    )


def _trn(name, kind, text="", catalog_id=None, image=None):
    from app.catalog import PREFERRED_IDS, _looks_like_tcgdex_id, _tcgdex_low

    cid = catalog_id or PREFERRED_IDS.get(name) or name.lower().replace(" ", "-")
    art = image
    if not art and _looks_like_tcgdex_id(str(cid or "")):
        try:
            art = _tcgdex_low(cid)
        except Exception:
            art = None
    return Card(
        catalog_id=cid,
        name=name,
        category="Trainer",
        stage=kind.title(),
        trainer_kind=kind,
        text=text,
        image=art,
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
_register(
    _trn(
        "Lillie",
        "supporter",
        "Draw cards until you have 6 cards in your hand. If it's your first turn, draw cards until you have 8 cards in your hand.",
    )
)
_register(_trn("Youngster", "supporter", "Shuffle your hand into your deck and draw 5 cards."))
_register(_trn("Shauna", "supporter", "Shuffle your hand into your deck and draw 5 cards."))
_register(
    _trn(
        "Professor's Research",
        "supporter",
        "Discard your hand and draw 7 cards.",
        catalog_id="sv01-189",
        image="https://assets.tcgdex.net/en/sv/sv01/189/low.webp",
    )
)
_RARE_CANDY_TEXT = (
    "Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card that evolves "
    "from that Pokémon in your hand, put that card onto the Basic Pokémon to evolve it, "
    "skipping the Stage 1. You can't use this card during your first turn or on a Basic "
    "Pokémon that was put into play this turn."
)
_register(_trn("Rare Candy", "item", _RARE_CANDY_TEXT))
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
_register(
    _trn(
        "Potion",
        "item",
        "Remove 2 damage counters from 1 of your Pokémon (remove 1 damage counter if that Pokémon has only 1).",
        catalog_id="dp7-92",
    )
)
_register(_trn("Energy Switch", "item", "Move a Basic Energy from 1 of your Pokémon to another of your Pokémon."))
_register(
    _trn(
        "Super Rod",
        "item",
        "Shuffle up to 3 in any combination of Pokémon and Basic Energy cards from your discard pile into your deck.",
    )
)
_register(
    Card(
        catalog_id="sv08-187",
        name="Surfer",
        category="Trainer",
        stage="Supporter",
        trainer_kind="supporter",
        text="Switch your Active Pokémon with 1 of your Benched Pokémon. If you do, draw cards until you have 5 cards in your hand.",
        image="https://assets.tcgdex.net/en/sv/sv08/187/low.webp",
        retreat=0,
    )
)
_register(
    Card(
        catalog_id="sv09-149",
        name="Iris's Fighting Spirit",
        category="Trainer",
        stage="Supporter",
        trainer_kind="supporter",
        text="You can use this card only if you discard another card from your hand. Draw cards until you have 6 cards in your hand.",
        image="https://assets.tcgdex.net/en/sv/sv09/149/low.webp",
        retreat=0,
    )
)
_register(
    Card(
        catalog_id="sv02-185",
        name="Iono",
        category="Trainer",
        stage="Supporter",
        trainer_kind="supporter",
        text="Each player shuffles their hand into their deck. Then, you draw a card for each of your remaining Prize cards, and your opponent does the same.",
        image="https://assets.tcgdex.net/en/sv/sv02/185/low.webp",
        retreat=0,
    )
)
_register(
    Card(
        catalog_id="sv02-178",
        name="Switch Cart",
        category="Trainer",
        stage="Item",
        trainer_kind="item",
        text="Switch your Active Pokémon with 1 of your Benched Pokémon. If you do, put this Pokémon on the bottom of your deck.",
        image="https://assets.tcgdex.net/en/sv/sv02/178/low.webp",
        retreat=0,
    )
)
_register(
    Card(
        catalog_id="sv07-139",
        name="Lacey",
        category="Trainer",
        stage="Supporter",
        trainer_kind="supporter",
        text="Shuffle your hand into your deck. Then, draw 4 cards. If your opponent has 3 or fewer Prize cards remaining, draw 8 cards instead.",
        image="https://assets.tcgdex.net/en/sv/sv07/139/low.webp",
        retreat=0,
    )
)
_register(
    Card(
        catalog_id="sv08-174",
        name="Drayton",
        category="Trainer",
        stage="Supporter",
        trainer_kind="supporter",
        text="Look at the top 7 cards of your deck. You may reveal a Pokémon and a Trainer card you find there and put them into your hand. Shuffle the other cards back into your deck.",
        image="https://assets.tcgdex.net/en/sv/sv08/174/low.webp",
        retreat=0,
    )
)
_register(
    _trn(
        "Earthen Vessel",
        "item",
        "Search your deck for up to 2 Basic Energy cards, reveal them, and put them into your hand. Then, shuffle your deck. You must discard a card from your hand in order to use this.",
    )
)
_register(_trn("Poké Ball", "item", "Flip a coin. If heads, search your deck for a Pokémon.", catalog_id="swsh3.5-59", image="https://assets.tcgdex.net/en/swsh/swsh3.5/59/low.webp"))
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
        "Rosa's Encouragement",
        "supporter",
        "You can use this card only if you have more Prize cards remaining than your opponent. Attach up to 2 Basic Energy cards from your discard pile to 1 of your Stage 2 Pokémon.",
        catalog_id="me03-084",
        image="https://assets.tcgdex.net/en/me/me03/084/low.webp",
    )
)
_register(
    _trn(
        "Special Red Card",
        "item",
        "You can use this card only if your opponent has 3 or fewer Prize cards remaining. Your opponent shuffles their hand and puts it on the bottom of their deck. If they put any cards on the bottom of their deck in this way, they draw 3 cards.",
        catalog_id="me04-082",
        image="https://assets.tcgdex.net/en/me/me04/082/low.webp",
    )
)
_register(
    _trn(
        "Risky Ruins",
        "stadium",
        "Whenever any player puts a Basic non-Darkness Pokémon onto their Bench during their turn, place 2 damage counters on that Pokémon.",
        catalog_id="me01-127",
        image="https://assets.tcgdex.net/en/me/me01/127/low.webp",
    )
)
_register(
    _trn(
        "Counter Catcher",
        "item",
        "You can use this card only if you have more Prize cards remaining than your opponent.\n\n"
        "Switch in 1 of your opponent's Benched Pokémon to the Active Spot.",
        catalog_id="sv04-160",
        image="https://assets.tcgdex.net/en/sv/sv04/160/low.webp",
    )
)
_register(
    _trn(
        "Forest Seal Stone",
        "item",
        "The Pokémon V this card is attached to can use the VSTAR Power on this card.\n\n"
        "Star Alchemy: During your turn, you may search your deck for a card and put it "
        "into your hand. Then, shuffle your deck. (You can't use more than 1 VSTAR Power in a game.)",
        catalog_id="swsh12-156",
        image="https://assets.tcgdex.net/en/swsh/swsh12/156/low.webp",
    )
)
_register(
    _trn(
        "Professor Turo's Scenario",
        "supporter",
        "Put 1 of your Pokémon into your hand. (Discard all attached cards.)",
        catalog_id="sv04-171",
        image="https://assets.tcgdex.net/en/sv/sv04/171/low.webp",
    )
)
_register(
    _trn(
        "Penny",
        "supporter",
        "Put 1 of your Basic Pokémon and all attached cards into your hand.",
        catalog_id="sv01-183",
        image="https://assets.tcgdex.net/en/sv/sv01/183/low.webp",
    )
)
_register(
    _trn(
        "AZ",
        "supporter",
        "Put 1 of your Pokémon into your hand. (Discard all cards attached to that Pokémon.)",
        catalog_id="xy4-91",
        image="https://assets.tcgdex.net/en/xy/xy4/91/low.webp",
    )
)
_register(
    _trn(
        "Cheren's Care",
        "supporter",
        "Put 1 of your Colorless Pokémon that has any damage counters on it and all attached cards into your hand.",
        catalog_id="swsh9-134",
        image="https://assets.tcgdex.net/en/swsh/swsh9/134/low.webp",
    )
)
_register(
    _trn(
        "Mr. Briney's Compassion",
        "supporter",
        "Choose 1 of your Pokémon in play (excluding Pokémon-ex). Return that Pokémon and all cards attached to it to your hand.",
        catalog_id="ex3-87",
        image="https://assets.tcgdex.net/en/ex/ex3/87/low.webp",
    )
)
_register(
    _trn(
        "Seeker",
        "supporter",
        "Each player returns 1 of his or her Benched Pokémon and all cards attached to it to his or her hand. (You return your Pokémon first.)",
        catalog_id="hgss3-85",
        image="https://assets.tcgdex.net/en/hgss/hgss3/85/low.webp",
    )
)
_register(
    _trn(
        "Collapsed Stadium",
        "stadium",
        "Each player can't have more than 4 Benched Pokémon. If a player has 5 or more "
        "Benched Pokémon, they discard Benched Pokémon until they have 4 Pokémon on the Bench. "
        "Your opponent discards first.",
        catalog_id="swsh9-137",
        image="https://assets.tcgdex.net/en/swsh/swsh9/137/low.webp",
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
_TELEPATHIC = _register(
    Card(
        catalog_id="me03-088",
        name="Telepathic Psychic Energy",
        category="Energy",
        stage="Special",
        types=["Psychic"],
        energy_type="Psychic",
        text=(
            "As long as this card is attached to a Pokémon, it provides Psychic Energy. "
            "When you attach this card from your hand to a Psychic Pokémon, search your deck "
            "for up to 2 Basic Psychic Pokémon and put them onto your Bench. Then, shuffle your deck."
        ),
        image="https://assets.tcgdex.net/en/me/me03/088/low.webp",
        set_name="Perfect Order",
        retreat=0,
    )
)
FALLBACK_BY_NAME["telepathic energy"] = _TELEPATHIC
FALLBACK_BY_NAME["telepathic psychic energy"] = _TELEPATHIC

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
        "Lillie's Clefairy ex",
        "Basic",
        ["Psychic"],
        190,
        [
            _atk(
                "Full Moon Rondo",
                ["Psychic", "Colorless"],
                20,
                "This attack does 20 more damage for each Benched Pokémon (both yours and your opponent's).",
            )
        ],
        catalog_id="sv09-056",
        weakness="Metal",
        retreat=1,
        abilities=[
            Ability(
                name="Fairy Zone",
                text=(
                    "The Weakness of each of your opponent's Dragon Pokémon in play is now Psychic. "
                    "(Apply Weakness as ×2.)"
                ),
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
        abilities=[
            Ability(
                name="Midnight Fluttering",
                text=(
                    "As long as this Pokémon is in the Active Spot, your opponent's Active Pokémon "
                    "has no Abilities, except for Midnight Fluttering."
                ),
            )
        ],
    ),
    _pkm("Hisuian Sliggoo", "Stage1", ["Dragon"], 90, [_atk("Rigidify", ["Colorless"], 0), _atk("Gentle Slap", ["Water", "Metal"], 40)], evolves_from="Goomy", weakness="Dragon"),
    _pkm("Sudowoodo", "Basic", ["Fighting"], 110, [
        _atk("Joust", ["Fighting"], 20),
        _atk("Impound", ["Fighting", "Colorless"], 50, "During your opponent's next turn, the Defending Pokémon can't retreat."),
    ], weakness="Water", catalog_id="swsh11-094"),
    _pkm("Gible", "Basic", ["Fighting"], 70, [_atk("Bite", ["Fighting"], 20)], weakness="Grass", catalog_id="sv04-094"),
    _pkm("Relicanth", "Basic", ["Fighting"], 90, [
        _atk(
            "Into the Deep",
            ["Colorless"],
            0,
            "Put up to 2 basic Energy cards from your discard pile into your hand.",
        ),
        _atk("Tackle", ["Colorless", "Colorless", "Colorless"], 80),
    ], weakness="Grass", catalog_id="swsh11-101"),
    _pkm(
        "Indeedee",
        "Basic",
        ["Colorless"],
        90,
        [
            _atk(
                "Expert Nurturer",
                ["Colorless"],
                0,
                "Search your deck for a card that evolves from 1 of your Pokémon and put it onto that "
                "Pokémon to evolve it. Then, shuffle your deck.",
            ),
            _atk(
                "Hypnoblast",
                ["Colorless", "Colorless"],
                30,
                "Your opponent's Active Pokémon is now Asleep.",
            ),
        ],
        weakness="Fighting",
        catalog_id="sv01-153",
    ),
    _pkm(
        "Trapinch",
        "Basic",
        ["Fighting"],
        60,
        [
            _atk(
                "Call for Family",
                ["Colorless"],
                0,
                "Search your deck for up to 2 Basic Pokémon and put them onto your Bench. Then, shuffle your deck.",
            ),
            _atk("Bite", ["Fighting", "Colorless"], 20),
        ],
        weakness="Grass",
        catalog_id="sv08-104",
    ),
    _pkm(
        "Kecleon",
        "Basic",
        ["Colorless"],
        70,
        [
            _atk(
                "Lick Whip",
                ["Colorless", "Colorless"],
                0,
                "This attack does 30 damage to 1 of your opponent's Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)",
            )
        ],
        weakness="Fighting",
        catalog_id="sv08-150",
        abilities=[
            Ability(
                name="Expert Hider",
                text="If any damage is done to this Pokémon by attacks, flip a coin. If heads, prevent that damage.",
            )
        ],
    ),
    _pkm(
        "Hop's Cramorant",
        "Basic",
        ["Colorless"],
        110,
        [
            _atk(
                "Fickle Spitting",
                ["Colorless"],
                120,
                "If your opponent doesn't have exactly 3 or 4 Prize cards remaining, this attack does nothing.",
            )
        ],
        weakness="Lightning",
        catalog_id="me02.5-177",
    ),
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
        image="https://assets.tcgdex.net/en/sv/sv04/087/low.webp",
    ),
    _pkm("Plusle", "Basic", ["Lightning"], 70, [_atk(
        "Plus Damage",
        ["Colorless", "Colorless"],
        10,
        "This attack does 10 more damage for each damage counter on your opponent's Active Pokémon.",
    )], weakness="Fighting", catalog_id="sv04-060"),
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
    _pkm(
        "Dedenne",
        "Basic",
        ["Psychic"],
        70,
        [
            _atk(
                "Dede-Flash",
                ["Psychic"],
                20,
                "If your opponent has exactly 1 Prize card remaining, this attack does 60 more damage, and your opponent's Active Pokémon is now Confused.",
            )
        ],
        weakness="Metal",
        catalog_id="swsh9-067",
        image="https://assets.tcgdex.net/en/swsh/swsh9/067/low.webp",
    ),
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
        "Ledyba",
        "Basic",
        ["Grass"],
        60,
        [_atk("Headbutt Bounce", ["Colorless", "Colorless"], 30)],
        weakness="Fire",
        catalog_id="sv07-002",
        image="https://assets.tcgdex.net/en/sv/sv07/002/low.webp",
    ),
    _pkm(
        "Ledian",
        "Stage1",
        ["Grass"],
        90,
        [
            _atk(
                "Swift",
                ["Colorless", "Colorless"],
                70,
                "This attack's damage isn't affected by Weakness or Resistance, or by any effects on your opponent's Active Pokémon.",
            )
        ],
        evolves_from="Ledyba",
        retreat=0,
        weakness="Fire",
        catalog_id="sv07-003",
        image="https://assets.tcgdex.net/en/sv/sv07/003/low.webp",
        abilities=[
            Ability(
                name="Glittering Star Pattern",
                text=(
                    "When you play this Pokémon from your hand to evolve 1 of your Pokémon during your turn, "
                    "you may switch in 1 of your opponent's Benched Pokémon that has 90 HP or less remaining "
                    "to the Active Spot."
                ),
            )
        ],
    ),
    _pkm(
        "Misdreavus",
        "Basic",
        ["Psychic"],
        50,
        [
            _atk(
                "Take Back",
                [],
                0,
                "Flip a coin. If heads, search your discard pile for a Trainer card, show it to your opponent, and put it into your hand.",
            ),
            _atk("Tackle", ["Colorless"], 10),
        ],
        weakness="Darkness",
        resistances=[{"type": "Colorless", "value": "-20"}],
        catalog_id="pl1-83",
        image="https://assets.tcgdex.net/en/pl/pl1/83/low.webp",
        set_name="Platinum",
    ),
    _pkm(
        "Mismagius",
        "Stage1",
        ["Psychic"],
        90,
        [
            _atk(
                "Upper Hand",
                ["Psychic"],
                30,
                "Choose 1 of the Defending Pokémon's attacks. That Pokémon can't use that attack during your opponent's next turn.",
            ),
            _atk(
                "Psybeam",
                ["Psychic", "Colorless", "Colorless"],
                60,
                "Flip a coin. If heads, the Defending Pokémon is now Confused.",
            ),
        ],
        evolves_from="Misdreavus",
        weakness="Darkness",
        resistances=[{"type": "Colorless", "value": "-20"}],
        catalog_id="pl1-55",
        image="https://assets.tcgdex.net/en/pl/pl1/55/low.webp",
        set_name="Platinum",
    ),
    _pkm(
        "Munkidori",
        "Basic",
        ["Psychic"],
        110,
        [
            _atk(
                "Mind Bend",
                ["Psychic", "Colorless"],
                60,
                "Your opponent's Active Pokémon is now Confused.",
            )
        ],
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="sv06-095",
        image="https://assets.tcgdex.net/en/sv/sv06/095/low.webp",
        abilities=[
            Ability(
                name="Adrena-Brain",
                text=(
                    "Once during your turn, if this Pokémon has any {D} Energy attached, "
                    "you may move up to 3 damage counters from 1 of your Pokémon to 1 of your opponent's Pokémon."
                ),
            )
        ],
    ),
    _pkm(
        "Scatterbug",
        "Basic",
        ["Grass"],
        40,
        [
            _atk(
                "Call for Family",
                ["Colorless"],
                0,
                "Search your deck for a Basic Pokémon and put it onto your Bench. Then, shuffle your deck.",
            )
        ],
        weakness="Fire",
        catalog_id="sv08-005",
        image="https://assets.tcgdex.net/en/sv/sv08/005/low.webp",
    ),
    _pkm(
        "Drifloon",
        "Basic",
        ["Psychic"],
        60,
        [
            _atk(
                "Triple Spin",
                ["Psychic"],
                10,
                "Flip 3 coins. This attack does 10 damage for each heads.",
            )
        ],
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="swsh10-063",
        image="https://assets.tcgdex.net/en/swsh/swsh10/063/low.webp",
    ),
    _pkm(
        "Drifblim",
        "Stage1",
        ["Psychic"],
        110,
        [
            _atk(
                "Spooky Balloon",
                ["Psychic"],
                50,
                "Put 2 damage counters on 1 of your opponent's Benched Pokémon.",
            )
        ],
        evolves_from="Drifloon",
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="swsh10-064",
        image="https://assets.tcgdex.net/en/swsh/swsh10/064/low.webp",
    ),
    _pkm(
        "Iron Boulder",
        "Basic",
        ["Psychic"],
        140,
        [
            _atk(
                "Adjusted Horn",
                ["Psychic", "Colorless"],
                170,
                "If you don't have the same number of cards in your hand as your opponent, this attack does nothing.",
            )
        ],
        retreat=3,
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="sv07-071",
        image="https://assets.tcgdex.net/en/sv/sv07/071/low.webp",
    ),
    _pkm(
        "Mewtwo",
        "Basic",
        ["Psychic"],
        130,
        [_atk("Super Psy Bolt", ["Psychic", "Psychic", "Colorless"], 100)],
        retreat=2,
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="sv07-059",
        image="https://assets.tcgdex.net/en/sv/sv07/059/low.webp",
    ),
    _pkm(
        "Tornadus",
        "Basic",
        ["Colorless"],
        110,
        [
            _atk("Knuckle Punch", ["Colorless", "Colorless"], 50),
            _atk(
                "Storm Barrier",
                ["Colorless", "Colorless", "Colorless"],
                100,
                "During your opponent's next turn, this Pokémon takes 50 less damage from attacks (after applying Weakness and Resistance).",
            ),
        ],
        retreat=1,
        weakness="Lightning",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="sv07-120",
        image="https://assets.tcgdex.net/en/sv/sv07/120/low.webp",
    ),
    _pkm(
        "Oranguru",
        "Basic",
        ["Colorless"],
        120,
        [
            _atk(
                "Now You're in My Power",
                ["Colorless"],
                0,
                "Until the end of your next turn, the Defending Pokémon's Weakness is now Colorless. (The amount of Weakness doesn't change.)",
            ),
            _atk("Smack", ["Colorless", "Colorless", "Colorless"], 80),
        ],
        retreat=2,
        weakness="Fighting",
        catalog_id="sv08-156",
        image="https://assets.tcgdex.net/en/sv/sv08/156/low.webp",
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
    _pkm(
        "Dunsparce",
        "Basic",
        ["Colorless"],
        70,
        [
            _atk(
                "Trading Places",
                ["Colorless"],
                0,
                "Switch this Pokémon with 1 of your Benched Pokémon.",
            ),
            _atk("Ram", ["Colorless", "Colorless"], 20),
        ],
        weakness="Fighting",
        catalog_id="sv09-120",
        image="https://assets.tcgdex.net/en/sv/sv09/120/low.webp",
        set_name="Journey Together",
    ),
    _pkm(
        "Dudunsparce",
        "Stage1",
        ["Colorless"],
        140,
        [_atk("Land Crush", ["Colorless", "Colorless", "Colorless"], 90)],
        evolves_from="Dunsparce",
        retreat=3,
        abilities=[
            Ability(
                name="Run Away Draw",
                text=(
                    "Once during your turn, you may draw 3 cards. If you drew any cards "
                    "in this way, shuffle this Pokémon and all attached cards into your deck."
                ),
            )
        ],
        weakness="Fighting",
        catalog_id="sv05-129",
        image="https://assets.tcgdex.net/en/sv/sv05/129/low.webp",
        set_name="Temporal Forces",
    ),
    _pkm(
        "Meowth ex",
        "Basic",
        ["Colorless"],
        170,
        [
            _atk(
                "Tuck Tail",
                ["Colorless", "Colorless", "Colorless"],
                60,
                "Put this Pokémon and all attached cards into your hand.",
            )
        ],
        abilities=[
            Ability(
                name="Last-Ditch Catch",
                text=(
                    "Once during your turn, when you play this Pokémon from your hand onto your Bench, "
                    "you may use this Ability. Search your deck for a Supporter card, reveal it, "
                    "and put it into your hand. Then, shuffle your deck. You can't use more than 1 "
                    "Ability that has \"Last-Ditch\" in its name each turn."
                ),
            )
        ],
        weakness="Fighting",
        catalog_id="me03-062",
        image="https://assets.tcgdex.net/en/me/me03/062/low.webp",
        set_name="Perfect Order",
    ),
    _pkm(
        "Pidgey",
        "Basic",
        ["Colorless"],
        60,
        [_atk("Gust", ["Colorless"], 20)],
        weakness="Lightning",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="sv03-162",
        image="https://assets.tcgdex.net/en/sv/sv03/162/low.webp",
        set_name="Obsidian Flames",
    ),
    _pkm(
        "Pidgeotto",
        "Stage1",
        ["Colorless"],
        80,
        [_atk("Wing Attack", ["Colorless", "Colorless"], 40)],
        evolves_from="Pidgey",
        weakness="Lightning",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="sv03-163",
        image="https://assets.tcgdex.net/en/sv/sv03/163/low.webp",
        set_name="Obsidian Flames",
    ),
    _pkm(
        "Pidgeot ex",
        "Stage2",
        ["Colorless"],
        280,
        [
            _atk(
                "Blustery Wind",
                ["Colorless", "Colorless"],
                120,
                "You may discard a Stadium in play.",
            )
        ],
        evolves_from="Pidgeotto",
        retreat=0,
        abilities=[
            Ability(
                name="Quick Search",
                text=(
                    "Once during your turn, you may search your deck for a card, reveal it, "
                    "and put it into your hand. Then, shuffle your deck. You can't use more "
                    "than 1 Quick Search Ability during your turn."
                ),
            )
        ],
        weakness="Lightning",
        resistances=[{"type": "Fighting", "value": "-30"}],
        catalog_id="sv03-164",
        image="https://assets.tcgdex.net/en/sv/sv03/164/low.webp",
        set_name="Obsidian Flames",
    ),
    _pkm(
        "Rotom V",
        "Basic",
        ["Lightning"],
        190,
        [
            _atk(
                "Scrap Short",
                ["Lightning", "Colorless"],
                40,
                "Put any number of Pokémon Tools attached to your Pokémon in the Lost Zone. "
                "This attack does 40 more damage for each card you put in the Lost Zone in this way.",
            )
        ],
        abilities=[
            Ability(
                name="Instant Charge",
                text=(
                    "Once during your turn, you may draw 3 cards. If you do, your turn ends."
                ),
            )
        ],
        weakness="Fighting",
        catalog_id="swsh11-058",
        image="https://assets.tcgdex.net/en/swsh/swsh11/058/low.webp",
        set_name="Lost Origin",
    ),
    _pkm(
        "Lumineon V",
        "Basic",
        ["Water"],
        170,
        [
            _atk(
                "Aqua Return",
                ["Colorless", "Colorless", "Colorless"],
                40,
                "Shuffle this Pokémon and all attached cards into your deck.",
            )
        ],
        abilities=[
            Ability(
                name="Luminous Sign",
                text=(
                    "When you play this Pokémon from your hand onto your Bench during your turn, "
                    "you may search your deck for a Supporter card, reveal it, and put it into "
                    "your hand. Then, shuffle your deck."
                ),
            )
        ],
        weakness="Lightning",
        catalog_id="swsh9-040",
        image="https://assets.tcgdex.net/en/swsh/swsh9/040/low.webp",
        set_name="Brilliant Stars",
    ),
    _pkm(
        "Manaphy",
        "Basic",
        ["Water"],
        70,
        [_atk("Rain Splash", ["Water"], 20)],
        abilities=[
            Ability(
                name="Wave Veil",
                text=(
                    "Prevent all damage done to your Benched Pokémon by attacks from "
                    "your opponent's Pokémon."
                ),
            )
        ],
        weakness="Lightning",
        catalog_id="swsh9-041",
        image="https://assets.tcgdex.net/en/swsh/swsh9/041/low.webp",
        set_name="Brilliant Stars",
    ),
    _pkm(
        "Glimmet",
        "Basic",
        ["Psychic"],
        50,
        [
            _atk("Ascension", ["Psychic"], 0, "Search your deck for a card that evolves from this Pokémon and put it onto this Pokémon to evolve it. Then, shuffle your deck."),
            _atk("Poison Shard", ["Psychic", "Colorless"], 20, "Your opponent's Active Pokémon is now Poisoned."),
        ],
        weakness="Darkness",
        catalog_id="sv02-124",
        image="https://assets.tcgdex.net/en/sv/sv02/124/low.webp",
    ),
    _pkm(
        "Gastly",
        "Basic",
        ["Psychic"],
        50,
        [_atk("Astonish", ["Psychic"], 10, "Choose a random card from your opponent's hand. Your opponent reveals that card and shuffles it into their deck.")],
        weakness="Darkness",
        catalog_id="sv06-055",
        image="https://assets.tcgdex.net/en/sv/sv06/055/low.webp",
    ),
    _pkm(
        "Haunter",
        "Stage1",
        ["Psychic"],
        80,
        [
            _atk("Pain Amplifier", ["Psychic"], 0, "Put 2 damage counters on each of your opponent's Pokémon that has any damage counters on it."),
            _atk("Spooky Shot", ["Psychic", "Colorless"], 40),
        ],
        evolves_from="Gastly",
        weakness="Darkness",
        catalog_id="sv06-056",
        image="https://assets.tcgdex.net/en/sv/sv06/056/low.webp",
    ),
    _pkm(
        "Gengar",
        "Stage2",
        ["Psychic"],
        130,
        [
            _atk(
                "Poltergeist",
                ["Psychic"],
                50,
                "Your opponent reveals their hand. This attack does 50 damage for each Trainer card you find there.",
            ),
            _atk("Deep Dive Haunt", ["Psychic", "Colorless"], 110),
        ],
        evolves_from="Haunter",
        weakness="Darkness",
        catalog_id="sv06-057",
        image="https://assets.tcgdex.net/en/sv/sv06/057/low.webp",
    ),
    _pkm(
        "Quaquaval",
        "Stage2",
        ["Water"],
        170,
        [
            _atk("Hydro Kick", ["Water", "Colorless", "Colorless"], 140),
        ],
        evolves_from="Quaxwell",
        abilities=[
            Ability(
                name="Energy Carnival",
                text="Once during your turn, you may attach a Basic Energy card from your hand to 1 of your Pokémon.",
            )
        ],
        weakness="Lightning",
        retreat=2,
        catalog_id="sv01-054",
        image="https://assets.tcgdex.net/en/sv/sv01/054/low.webp",
    ),
    _pkm(
        "Hippopotas",
        "Basic",
        ["Fighting"],
        100,
        [_atk("Tackle", ["Fighting", "Colorless"], 30), _atk("Mud Shot", ["Fighting", "Fighting", "Colorless"], 50)],
        retreat=4,
        weakness="Grass",
        catalog_id="swsh7-084",
        image="https://assets.tcgdex.net/en/swsh/swsh7/084/low.webp",
    ),
    _pkm(
        "Skwovet",
        "Basic",
        ["Colorless"],
        60,
        [_atk("Gnaw", ["Colorless"], 10), _atk("Bite", ["Colorless", "Colorless"], 20)],
        weakness="Fighting",
        catalog_id="sv01-151",
        image="https://assets.tcgdex.net/en/sv/sv01/151/low.webp",
    ),
    _pkm(
        "Scream Tail",
        "Basic",
        ["Psychic"],
        90,
        [
            _atk("Slap", ["Psychic"], 30),
            _atk("Roaring Scream", ["Psychic", "Colorless"], 0, "This attack does 20 damage to 1 of your opponent's Pokémon for each damage counter on this Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)"),
        ],
        weakness="Darkness",
        catalog_id="sv04-086",
        image="https://assets.tcgdex.net/en/sv/sv04/086/low.webp",
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
    image="https://assets.tcgdex.net/en/base/base1/5/low.webp",
)
FALLBACK_BY_NAME["clefable twm"] = _CLEFABLE_TWM
FALLBACK_BY_NAME["clefable (twilight masquerade)"] = _CLEFABLE_TWM
FALLBACK_BY_NAME["clefable clc"] = _CLEFABLE_CLC
FALLBACK_BY_NAME["clefable (clc 014)"] = _CLEFABLE_CLC
FALLBACK_BY_NAME["clefable cmc 014"] = _CLEFABLE_CLC

_CELEBRATION_TEXT = (
    "If you have exactly 30 cards in your hand, take 2 Prize cards. If you do, shuffle your hand into your deck."
)
_CRAZY_CODE_TEXT = (
    "As often as you like during your turn (before your attack), you may attach a "
    "Special Energy card from your hand to 1 of your Pokémon."
)
_TELEPORTER_TEXT = (
    "Once during your turn, if this Pokémon is in the Active Spot, you may shuffle it "
    "and all attached cards into your deck."
)
_ENRICHING_TEXT = (
    "As long as this card is attached to a Pokémon, it provides Colorless Energy. "
    "When you attach this card from your hand to a Pokémon, draw 4 cards."
)
_SPEED_L_TEXT = (
    "As long as this card is attached to a Pokémon, it provides Lightning Energy. "
    "When you attach this card from your hand to a Lightning Pokémon, draw 2 cards."
)
_DRAW_ENERGY_TEXT = (
    "This card provides Colorless Energy. "
    "When you attach this card from your hand to a Pokémon, draw a card."
)
_FLEET_FOOTED_TEXT = (
    "Once during your turn, if this Pokémon is in the Active Spot, you may draw a card."
)
_LIGHTNING_STREAK_TEXT = "You may switch this Pokémon with 1 of your Benched Pokémon."
_HAND_FLING_TEXT = "This attack does 20 damage for each card in your hand."
_PUZZLE_TEXT = (
    "You may play 2 Puzzle of Time cards at once.\n"
    "• If you played 1 card, look at the top 3 cards of your deck and put them back in any order.\n"
    "• If you played 2 cards, put 2 cards from your discard pile into your hand."
)
_NET_TEXT = (
    "Put 1 of your Pokémon that isn't a Pokémon V or a Pokémon-GX into your hand. "
    "(Discard all attached cards.)"
)
_BTS_TEXT = (
    "Each player may evolve a Pokémon that he or she just played or evolved during that turn."
)
_WALLY_TEXT = (
    "Search your deck for a card that evolves from 1 of your Pokémon (excluding Pokémon-EX) "
    "and put it onto that Pokémon. (This counts as evolving that Pokémon.) Shuffle your deck afterward. "
    "You can use this card during your first turn or on a Pokémon that was put into play this turn."
)
_ABYSSAL_TEXT = (
    "Once during your turn (before your attack), you may draw cards until you have 5 cards in your hand."
)
_JUNK_HUNT_TEXT = "Put 2 Item cards from your discard pile into your hand."
_JUNK_ARM_TEXT = (
    "Discard 2 cards from your hand. Search your discard pile for a Trainer card, show it to your "
    "opponent, and put it in your hand. You can't choose Junk Arm with this effect."
)
_MEMORY_HELIX_TEXT = (
    "This Pokémon can use the attacks of any of your Benched Pokémon. "
    "(You still need the necessary Energy to use each attack.)"
)
_BIG_JUMP_TEXT = (
    "Once during your turn (before your attack), you may return this Pokémon "
    "and all cards attached to it to your hand."
)
_VS_SEEKER_TEXT = "Put a Supporter card from your discard pile into your hand."
_COMPRESSOR_TEXT = "Search your deck for up to 3 cards and discard them. Shuffle your deck afterward."

_register(
    _pkm(
        "Abra",
        "Basic",
        ["Psychic"],
        40,
        [_atk("Psyshot", ["Psychic"], 10)],
        retreat=1,
        catalog_id="sv06-080",
        weakness="Darkness",
        abilities=[Ability(name="Teleporter", text=_TELEPORTER_TEXT)],
        image="https://assets.tcgdex.net/en/sv/sv06/080/low.webp",
        set_name="Twilight Masquerade",
    )
)
_register(
    _pkm(
        "Buneary",
        "Basic",
        ["Colorless"],
        60,
        [
            _atk(
                "Bounce",
                ["Colorless", "Colorless"],
                10,
                "Switch this Pokémon with 1 of your Benched Pokémon.",
            )
        ],
        catalog_id="xy2-84",
        weakness="Fighting",
        image="https://assets.tcgdex.net/en/xy/xy2/84/low.webp",
        set_name="Flashfire",
    )
)
_register(
    _pkm(
        "Lopunny",
        "Stage1",
        ["Colorless"],
        90,
        [
            _atk(
                "Sitdown Bounce",
                ["Colorless", "Colorless", "Colorless"],
                80,
                "Flip a coin. If tails, this Pokémon can't attack during your next turn.",
            )
        ],
        evolves_from="Buneary",
        catalog_id="xy2-85",
        weakness="Fighting",
        abilities=[Ability(name="Big Jump", text=_BIG_JUMP_TEXT)],
        image="https://assets.tcgdex.net/en/xy/xy2/85/low.webp",
        set_name="Flashfire",
    )
)
_register(
    _pkm(
        "Hoppip",
        "Basic",
        ["Grass"],
        30,
        [
            _atk(
                "Flail Around",
                ["Grass"],
                10,
                "Flip 3 coins. This attack does 10 damage times the number of heads.",
            )
        ],
        catalog_id="bw6-1",
        weakness="Fire",
        resistances=[{"type": "Water", "value": "-20"}],
        image="https://assets.tcgdex.net/en/bw/bw6/1/low.webp",
        set_name="Dragons Exalted",
    )
)
_register(
    _pkm(
        "Skiploom",
        "Stage1",
        ["Grass"],
        60,
        [
            _atk(
                "Bullet Seed",
                ["Grass"],
                10,
                "Flip 4 coins. This attack does 10 damage times the number of heads.",
            )
        ],
        evolves_from="Hoppip",
        catalog_id="bw6-2",
        weakness="Fire",
        resistances=[{"type": "Water", "value": "-20"}],
        retreat=0,
        image="https://assets.tcgdex.net/en/bw/bw6/2/low.webp",
        set_name="Dragons Exalted",
    )
)
_register(
    _pkm(
        "Jumpluff",
        "Stage2",
        ["Grass"],
        90,
        [
            _atk(
                "Acrobatics",
                ["Grass"],
                20,
                "Flip 2 coins. This attack does 30 more damage for each heads.",
            )
        ],
        evolves_from="Skiploom",
        catalog_id="bw6-3",
        weakness="Fire",
        resistances=[{"type": "Water", "value": "-20"}],
        retreat=0,
        abilities=[Ability(name="Leave It to the Wind", text=_BIG_JUMP_TEXT)],
        image="https://assets.tcgdex.net/en/bw/bw6/3/low.webp",
        set_name="Dragons Exalted",
    )
)
_register(
    _pkm(
        "Porygon",
        "Basic",
        ["Colorless"],
        50,
        [_atk("Sharpshooting", ["Colorless"], 20)],
        catalog_id="sm10-154",
        weakness="Fighting",
        image="https://assets.tcgdex.net/en/sm/sm10/154/low.webp",
        set_name="Unbroken Bonds",
    )
)
_register(
    _pkm(
        "Porygon2",
        "Stage1",
        ["Colorless"],
        80,
        [_atk("Double Draw", ["Colorless"], 0, "Draw 2 cards.")],
        evolves_from="Porygon",
        catalog_id="sm10-156",
        weakness="Fighting",
        image="https://assets.tcgdex.net/en/sm/sm10/156/low.webp",
        set_name="Unbroken Bonds",
    )
)
_register(
    _pkm(
        "Porygon-Z",
        "Stage2",
        ["Colorless"],
        130,
        [
            _atk(
                "Tantrum",
                ["Colorless", "Colorless", "Colorless"],
                120,
                "This Pokémon is now Confused.",
            )
        ],
        evolves_from="Porygon2",
        catalog_id="sm10-157",
        weakness="Fighting",
        retreat=2,
        abilities=[Ability(name="Crazy Code", text=_CRAZY_CODE_TEXT)],
        image="https://assets.tcgdex.net/en/sm/sm10/157/low.webp",
        set_name="Unbroken Bonds",
    )
)
_register(
    _pkm(
        "Remoraid",
        "Basic",
        ["Water"],
        60,
        [_atk("Water Gun", ["Water"], 10)],
        catalog_id="xy5-32",
        weakness="Grass",
        image="https://assets.tcgdex.net/en/xy/xy5/32/low.webp",
        set_name="Primal Clash",
    )
)
_register(
    _pkm(
        "Octillery",
        "Stage1",
        ["Water"],
        90,
        [_atk("Ink Cannon", ["Water", "Colorless"], 30)],
        evolves_from="Remoraid",
        catalog_id="xy5-33",
        weakness="Grass",
        abilities=[Ability(name="Abyssal Hand", text=_ABYSSAL_TEXT)],
        image="https://assets.tcgdex.net/en/xy/xy5/33/low.webp",
        set_name="Primal Clash",
    )
)
_register(
    _pkm(
        "Sableye",
        "Basic",
        ["Darkness"],
        70,
        [_atk("Junk Hunt", ["Darkness"], 0, _JUNK_HUNT_TEXT)],
        catalog_id="bw6-62",
        weakness="Fighting",
        image="https://assets.tcgdex.net/en/bw/bw6/62/low.webp",
        set_name="Dark Explorers",
    )
)
_GIMMIGHOUL_30TH = _pkm(
    "Gimmighoul",
    "Basic",
    ["Metal"],
    60,
    [_atk("Astonish", ["Colorless"], 10)],
    catalog_id="30th-081",
    weakness="Fire",
    resistances=[{"type": "Grass", "value": "-30"}],
    image="https://assets.tcgdex.net/en/me/30th/081/low.webp",
    set_name="30th Celebration",
)
FALLBACK_BY_NAME["gimmighoul 30th"] = _GIMMIGHOUL_30TH
FALLBACK_BY_NAME["gimmighoul celebration"] = _GIMMIGHOUL_30TH
_register(
    _pkm(
        "Gholdengo",
        "Stage1",
        ["Metal"],
        130,
        [
            _atk("Celebration", ["Metal"], 0, _CELEBRATION_TEXT),
            _atk(
                "Triple Smash",
                ["Metal"],
                50,
                "Flip 3 coins. This attack does 50 damage for each heads.",
            ),
        ],
        evolves_from="Gimmighoul",
        catalog_id="30th-108",
        weakness="Fire",
        resistances=[{"type": "Grass", "value": "-30"}],
        retreat=2,
        image="https://assets.tcgdex.net/en/me/30th/108/low.webp",
        set_name="30th Celebration",
    )
)
_register(
    _pkm(
        "Mew ex",
        "Basic",
        ["Psychic"],
        160,
        [
            _atk(
                "Teleportation Burst",
                ["Psychic"],
                30,
                "You may switch this Pokémon with 1 of your Benched Pokémon.",
            )
        ],
        catalog_id="30th-066",
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        retreat=0,
        abilities=[Ability(name="Memory Helix", text=_MEMORY_HELIX_TEXT)],
        image="https://assets.tcgdex.net/en/me/30th/066/low.webp",
        set_name="30th Celebration",
    )
)
_register(
    _pkm(
        "Igglybuff",
        "Basic",
        ["Colorless"],
        30,
        [
            _atk(
                "Bouncy Circle",
                [],
                0,
                "This attack does 30 damage for each of your Benched Pokémon that has a maximum HP of 30.",
            )
        ],
        catalog_id="30th-120",
        retreat=0,
        image="https://assets.tcgdex.net/en/me/30th/120/low.webp",
        set_name="30th Celebration",
    )
)
_register(
    _pkm(
        "Mime Jr.",
        "Basic",
        ["Psychic"],
        30,
        [
            _atk(
                "Mimed Games",
                [],
                0,
                "Your opponent chooses an attack from 1 of their Pokémon in play. Use the chosen attack as this attack.",
            )
        ],
        catalog_id="sv04.5-031",
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        retreat=0,
        image="https://assets.tcgdex.net/en/sv/sv04.5/031/low.webp",
        set_name="Paldean Fates",
    )
)
_register(
    _pkm(
        "Cleffa",
        "Basic",
        ["Psychic"],
        30,
        [
            _atk(
                "Grasping Draw",
                [],
                0,
                "Draw cards until you have 7 cards in your hand.",
            )
        ],
        catalog_id="sv03-080",
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        retreat=0,
        image="https://assets.tcgdex.net/en/sv/sv03/080/low.webp",
        set_name="Obsidian Flames",
    )
)
_register(
    _pkm(
        "Radiant Charizard",
        "Basic",
        ["Fire"],
        160,
        [
            _atk(
                "Combustion Blast",
                ["Fire", "Colorless", "Colorless", "Colorless"],
                250,
                "During your next turn, this Pokémon can't use Combustion Blast.",
            )
        ],
        catalog_id="pgo-011",
        weakness="Water",
        retreat=3,
        abilities=[
            Ability(
                name="Excited Heart",
                text="This Pokémon's attacks cost Colorless less for each Prize card your opponent has taken.",
            )
        ],
        image="https://assets.tcgdex.net/en/pgo/pgo/011/low.webp",
        set_name="Pokémon GO",
    )
)
_register(
    _pkm(
        "Slaking V",
        "Basic",
        ["Colorless"],
        230,
        [
            _atk(
                "Heavy Impact",
                ["Colorless", "Colorless", "Colorless", "Colorless"],
                260,
                "",
            )
        ],
        catalog_id="pgo-058",
        weakness="Fighting",
        retreat=3,
        image="https://assets.tcgdex.net/en/pgo/pgo/058/low.webp",
        set_name="Pokémon GO",
    )
)
_register(
    _pkm(
        "Snorlax",
        "Basic",
        ["Colorless"],
        150,
        [
            _atk(
                "Rolling Tackle",
                ["Colorless", "Colorless", "Colorless"],
                100,
                "",
            )
        ],
        catalog_id="pgo-055",
        weakness="Fighting",
        retreat=4,
        image="https://assets.tcgdex.net/en/pgo/pgo/055/low.webp",
        set_name="Pokémon GO",
    )
)
_register(
    _pkm(
        "Dunsparce",
        "Basic",
        ["Colorless"],
        60,
        [
            _atk(
                "Sudden Flash",
                ["Colorless"],
                10,
                "Your opponent's Active Pokémon is now Paralyzed.",
            )
        ],
        catalog_id="mew-156",
        weakness="Fighting",
        retreat=1,
        image="https://assets.tcgdex.net/en/sv/sv03.5/156/low.webp",
        set_name="151",
    )
)
_register(
    _pkm(
        "Regigigas",
        "Basic",
        ["Colorless"],
        150,
        [
            _atk(
                "Giga Impact",
                ["Colorless", "Colorless", "Colorless", "Colorless", "Colorless"],
                230,
                "During your next turn, this Pokémon can't attack.",
            )
        ],
        catalog_id="crz-113",
        weakness="Fighting",
        retreat=4,
        image="https://assets.tcgdex.net/en/swsh/swsh12.5/113/low.webp",
        set_name="Crown Zenith",
    )
)
_register(
    _pkm(
        "Blissey ex",
        "Stage1",
        ["Colorless"],
        300,
        [
            _atk(
                "Return",
                ["Colorless", "Colorless", "Colorless"],
                180,
                "Draw cards until you have 6 cards in your hand.",
            )
        ],
        catalog_id="twm-134",
        weakness="Fighting",
        retreat=4,
        image="https://assets.tcgdex.net/en/sv/sv06/134/low.webp",
        set_name="Twilight Masquerade",
    )
)
_register(
    _trn(
        "Dimension Valley",
        "stadium",
        "The attacks of each Psychic Pokémon in play (both yours and your opponent's) cost Colorless less.",
        catalog_id="phf-093",
        image="https://assets.tcgdex.net/en/xy/xy4/093/low.webp",
    )
)
_register(
    _pkm(
        "Dodrio",
        "Stage1",
        ["Colorless"],
        100,
        [
            _atk(
                "Ballistic Beak",
                ["Colorless"],
                10,
                "This attack does 30 more damage for each damage counter on this Pokémon.",
            )
        ],
        catalog_id="me01-085",
        weakness="Lightning",
        resistances=[{"type": "Fighting", "value": "-30"}],
        retreat=1,
        image="https://assets.tcgdex.net/en/sv/sv03.5/085/low.webp",
        set_name="151",
    )
)
_register(
    _pkm(
        "Hisuian Zorua",
        "Basic",
        ["Psychic"],
        60,
        [
            _atk("Collect", [], 0, "Draw a card.")
        ],
        catalog_id="lor-075",
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        retreat=1,
        image="https://assets.tcgdex.net/en/swsh/swsh11/075/low.webp",
        set_name="Lost Origin",
    )
)
_register(
    _pkm(
        "Hisuian Zoroark",
        "Stage1",
        ["Psychic"],
        100,
        [
            _atk(
                "Doom Curse",
                [],
                0,
                "At the end of your opponent's next turn, the Defending Pokémon will be Knocked Out.",
            )
        ],
        catalog_id="lor-076",
        weakness="Darkness",
        resistances=[{"type": "Fighting", "value": "-30"}],
        retreat=2,
        image="https://assets.tcgdex.net/en/swsh/swsh11/076/low.webp",
        set_name="Lost Origin",
    )
)
_register(
    _trn(
        "Puzzle of Time",
        "item",
        _PUZZLE_TEXT,
        catalog_id="xy8-109",
        image="https://assets.tcgdex.net/en/xy/xy8/109/low.webp",
    )
)
_register(
    _trn(
        "Scoop Up Net",
        "item",
        _NET_TEXT,
        catalog_id="swsh5-165",
        image="https://assets.tcgdex.net/en/swsh/swsh5/165/low.webp",
    )
)
_register(
    _trn(
        "Junk Arm",
        "item",
        _JUNK_ARM_TEXT,
        catalog_id="hgss4-87",
        image="https://assets.tcgdex.net/en/hgss/hgss4/87/low.webp",
    )
)
_register(
    _trn(
        "Broken Time-Space",
        "stadium",
        _BTS_TEXT,
        catalog_id="pl1-104",
        image="https://assets.tcgdex.net/en/pl/pl1/104/low.webp",
    )
)
_register(
    _trn(
        "Wally",
        "supporter",
        _WALLY_TEXT,
        catalog_id="xy6-94",
        image="https://assets.tcgdex.net/en/xy/xy6/94/low.webp",
    )
)
_register(
    _trn(
        "VS Seeker",
        "item",
        _VS_SEEKER_TEXT,
        catalog_id="xy4-109",
        image="https://assets.tcgdex.net/en/xy/xy4/109/low.webp",
    )
)
_register(
    _trn(
        "Battle Compressor",
        "item",
        _COMPRESSOR_TEXT,
        catalog_id="xy3-92",
        image="https://assets.tcgdex.net/en/xy/xy3/92/low.webp",
    )
)
_ENRICHING = _register(
    Card(
        catalog_id="sv08-191",
        name="Enriching Energy",
        category="Energy",
        stage="Special",
        types=["Colorless"],
        energy_type="Colorless",
        text=_ENRICHING_TEXT,
        image="https://assets.tcgdex.net/en/sv/sv08/191/low.webp",
        set_name="Surging Sparks",
        retreat=0,
    )
)
FALLBACK_BY_NAME["enriching energy"] = _ENRICHING
_SPEED_L = _register(
    Card(
        catalog_id="swsh2-173",
        name="Speed Lightning Energy",
        category="Energy",
        stage="Special",
        types=["Lightning"],
        energy_type="Lightning",
        text=_SPEED_L_TEXT,
        image="https://assets.tcgdex.net/en/swsh/swsh2/173/low.webp",
        set_name="Rebel Clash",
        retreat=0,
    )
)
FALLBACK_BY_NAME["speed lightning energy"] = _SPEED_L
FALLBACK_BY_NAME["speed l energy"] = _SPEED_L
_DRAW_ENERGY = _register(
    Card(
        catalog_id="sm12-209",
        name="Draw Energy",
        category="Energy",
        stage="Special",
        types=["Colorless"],
        energy_type="Colorless",
        text=_DRAW_ENERGY_TEXT,
        image="https://assets.tcgdex.net/en/sm/sm12/209/low.webp",
        set_name="Cosmic Eclipse",
        retreat=0,
    )
)
FALLBACK_BY_NAME["draw energy"] = _DRAW_ENERGY
_register(
    _pkm(
        "Raikou V",
        "Basic",
        ["Lightning"],
        200,
        [
            _atk(
                "Lightning Streak",
                ["Lightning", "Colorless"],
                40,
                _LIGHTNING_STREAK_TEXT,
            )
        ],
        retreat=1,
        catalog_id="swsh9-48",
        weakness="Fighting",
        abilities=[Ability(name="Fleet-Footed", text=_FLEET_FOOTED_TEXT)],
        image="https://assets.tcgdex.net/en/swsh/swsh9/48/low.webp",
        set_name="Brilliant Stars",
    )
)

_AIPOM_PAR = _pkm(
    "Aipom",
    "Basic",
    ["Colorless"],
    60,
    [
        _atk("Filch", ["Colorless"], 0, "Draw a card."),
        _atk("Smack", ["Colorless", "Colorless"], 20),
    ],
    catalog_id="sv04-145",
    weakness="Fighting",
    image="https://assets.tcgdex.net/en/sv/sv04/145/low.webp",
    set_name="Paradox Rift",
)
FALLBACK_BY_NAME["aipom par"] = _AIPOM_PAR
FALLBACK_BY_NAME["aipom paradox"] = _AIPOM_PAR
_register(
    _pkm(
        "Ambipom",
        "Stage1",
        ["Colorless"],
        100,
        [
            _atk("Collect", ["Colorless"], 0, "Draw 2 cards."),
            _atk(
                "Hand Fling",
                ["Colorless", "Colorless", "Colorless"],
                20,
                _HAND_FLING_TEXT,
            ),
        ],
        evolves_from="Aipom",
        catalog_id="sv04-146",
        weakness="Fighting",
        image="https://assets.tcgdex.net/en/sv/sv04/146/low.webp",
        set_name="Paradox Rift",
    )
)


# Bench-shield package for C60 vs Dragapult (printed Standard text).
# Rellor TEF 23 / Rabsca TEF 24: Spherical Shield blocks bench damage AND attack
# effects (Phantom Dive counters). Shaymin DRI 10: Flower Curtain blocks bench
# damage to non-Rule-Box only (not counters). Battle Cage ME02 85: both benches
# ignore counter placement from opp attack/ability effects; damage still taken.
_register(
    _pkm(
        "Rellor",
        "Basic",
        ["Grass"],
        50,
        [_atk("Slight Intrusion", ["Colorless"], 30, "This Pokémon also does 10 damage to itself.")],
        catalog_id="sv05-023",
        weakness="Fire",
        retreat=1,
        set_name="Temporal Forces",
    )
)
_register(
    _pkm(
        "Rabsca",
        "Stage1",
        ["Grass"],
        70,
        [
            _atk(
                "Psychic",
                ["Grass"],
                "10+",
                "This attack does 30 more damage for each Energy attached to your opponent's Active Pokémon.",
            )
        ],
        evolves_from="Rellor",
        catalog_id="sv05-024",
        weakness="Fire",
        retreat=1,
        abilities=[
            Ability(
                name="Spherical Shield",
                text="Prevent all damage from and effects of attacks from your opponent's Pokémon done to your Benched Pokémon.",
            )
        ],
        set_name="Temporal Forces",
    )
)
_register(
    _pkm(
        "Shaymin",
        "Basic",
        ["Grass"],
        80,
        [_atk("Smash Kick", ["Colorless", "Colorless"], 30)],
        catalog_id="sv10-010",
        weakness="Fire",
        retreat=1,
        abilities=[
            Ability(
                name="Flower Curtain",
                text="Prevent all damage done to your Benched Pokémon that don't have a Rule Box by attacks from your opponent's Pokémon. (Pokémon ex, Pokémon V, etc. have Rule Boxes.)",
            )
        ],
        set_name="Destined Rivals",
    )
)
_register(
    _trn(
        "Battle Cage",
        "stadium",
        "Prevent all damage counters from being placed on Benched Pokémon (both yours and your opponent's) by effects of attacks and Abilities from the opponent's Pokémon. (Damage from attacks is still taken.)",
        catalog_id="me02-085",
        image="https://assets.tcgdex.net/en/me/me02/085/low.webp",
    )
)


def build_g30_deck() -> list[Card]:
    """Ambipom PAR 146 closer; Aipom uses the Paradox Rift print, not Lost Origin."""
    out: list[Card] = []
    for name in SET_G30_NAMES:
        if name == "Aipom":
            out.append(fallback_named("aipom par"))
        else:
            out.append(fallback_named(name))
    return out


# 151 / MEW 035 keeps the printed name "Clefairy" so it shares the 4-of cap
# with LOR 62 Moon-Watching Party. Alias keys so it does not overwrite Party.
_CLEFAIRY_MEW = _pkm(
    "Clefairy",
    "Basic",
    ["Psychic"],
    60,
    [
        _atk(
            "Moon-Viewing Invitation",
            ["Psychic"],
            0,
            "Search your deck for up to 3 Clefairy and put them onto your Bench. Then, shuffle your deck.",
        ),
        _atk("Smack", ["Psychic", "Colorless"], 20),
    ],
    catalog_id="sv03.5-035",
    weakness="Metal",
    retreat=1,
    set_name="151",
)
FALLBACK_BY_NAME["clefairy mew"] = _CLEFAIRY_MEW
FALLBACK_BY_NAME["clefairy 151"] = _CLEFAIRY_MEW
FALLBACK_BY_NAME["clefairy invitation"] = _CLEFAIRY_MEW
FALLBACK_BY_NAME["clefairy mew 035"] = _CLEFAIRY_MEW

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
    image="https://assets.tcgdex.net/en/sm/sm3/40/low.webp",
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
    image="https://assets.tcgdex.net/en/sm/sm12/66/low.webp",
)

# Carpet Set H: Destined Rivals Team Rocket's Zapdos (printed name is not Zapdos).
_register(_pkm(
    "Team Rocket's Zapdos",
    "Basic",
    ["Lightning"],
    120,
    [
        _atk(
            "Jamming Wing",
            ["Colorless", "Colorless"],
            30,
            "You may move an Energy from your opponent's Active Pokémon to 1 of their Benched Pokémon.",
        ),
        _atk(
            "Wicked Thunder",
            ["Lightning", "Colorless", "Colorless"],
            60,
            "If this Pokémon has any Team Rocket's Energy attached, this attack does 60 more damage.",
        ),
    ],
    catalog_id="sv10-070",
    weakness="Lightning",
    image="https://assets.tcgdex.net/en/sv/sv10/070/low.webp",
    resistances=[{"type": "Fighting", "value": "-30"}],
))

# Carpet Set H: Paradox Rift Zekrom — Hidden Fates sm3.5-35 has no TCGDex picture.
_register(_pkm(
    "Zekrom",
    "Basic",
    ["Lightning"],
    130,
    [
        _atk(
            "Crushing Short",
            ["Lightning"],
            20,
            "Before doing damage, discard all Pokémon Tools from your opponent's Active Pokémon.",
        ),
        _atk(
            "Raging Thunder",
            ["Lightning", "Lightning", "Colorless"],
            130,
            "This attack also does 40 damage to 1 of your Benched Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)",
        ),
    ],
    catalog_id="sv04-066",
    weakness="Fighting",
    image="https://assets.tcgdex.net/en/sv/sv04/066/low.webp",
))

# Set G carpet Starly: Brilliant Stars Claw 30 (Set A/F keep Paldea Evolved Flap).
FALLBACK_BY_NAME["starly-claw"] = _pkm(
    "Starly",
    "Basic",
    ["Colorless"],
    60,
    [
        _atk(
            "Claw",
            ["Colorless"],
            30,
            "Flip a coin. If tails, this attack does nothing.",
        )
    ],
    weakness="Lightning",
    catalog_id="swsh9-117",
    image="https://assets.tcgdex.net/en/swsh/swsh9/117/low.webp",
    resistances=[{"type": "Fighting", "value": "-30"}],
)

# Set G remaining 90 HP Staravia (Brilliant Stars). Paldea Evolved 80 HP stays the default.
FALLBACK_BY_NAME["staravia-brilliant"] = _pkm(
    "Staravia",
    "Stage1",
    ["Colorless"],
    90,
    [_atk("Wing Attack", ["Colorless", "Colorless"], 50)],
    evolves_from="Starly",
    weakness="Lightning",
    catalog_id="swsh9-118",
    image="https://assets.tcgdex.net/en/swsh/swsh9/118/low.webp",
    resistances=[{"type": "Fighting", "value": "-30"}],
)
FALLBACK_BY_NAME["mime jr"] = FALLBACK_BY_NAME["mime jr."]


def fallback_named(name: str) -> Card:
    key = name.lower()
    if "telepathic" in key:
        key = "telepathic psychic energy"
    if "double colorless" in key:
        key = "double colorless energy"
    if "boomerang" in key:
        key = "boomerang energy"
    if "enriching" in key:
        key = "enriching energy"
    if "speed lightning" in key or key in {"speed l energy", "speed l"}:
        key = "speed lightning energy"
    if key == "draw energy":
        key = "draw energy"
    if key in FALLBACK_BY_NAME:
        card = FALLBACK_BY_NAME[key]
        return Card.from_dict(card.to_dict())
    if (
        key.endswith(" energy")
        and "double" not in key
        and "boomerang" not in key
        and "telepathic" not in key
        and "enriching" not in key
        and "speed lightning" not in key
        and "speed l" not in key
        and key != "draw energy"
    ):
        return _nrg(name.split()[0].title())
    from app.catalog import fallback_card

    return fallback_card(name)


def build_fallback_deck(names: list[str]) -> list[Card]:
    return [fallback_named(n) for n in names]
