from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


ENERGY_TYPES = (
    "Grass",
    "Fire",
    "Water",
    "Lightning",
    "Psychic",
    "Fighting",
    "Darkness",
    "Metal",
    "Fairy",
    "Dragon",
    "Colorless",
)


@dataclass
class Attack:
    name: str
    cost: list[str]
    damage: int = 0
    text: str = ""
    effects: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Attack:
        text = data.get("text") or data.get("effect") or ""
        damage = int(data.get("damage") or 0)
        stored = list(data.get("effects") or [])
        # Printed text wins over stale seed JSON (empty or outdated effects).
        from app.engine.effects import parse_effects

        parsed = parse_effects(text, str(data.get("damage") or damage or ""))
        return cls(
            name=data.get("name", "Attack"),
            cost=list(data.get("cost") or ["Colorless"]),
            damage=damage,
            text=text,
            effects=parsed if parsed else stored,
        )


@dataclass
class Ability:
    name: str
    text: str = ""
    effects: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ability:
        text = data.get("text") or data.get("effect") or ""
        stored = list(data.get("effects") or [])
        from app.engine.effects import parse_ability_effects

        parsed = parse_ability_effects(text)
        return cls(
            name=data.get("name", "Ability"),
            text=text,
            effects=parsed if parsed else stored,
        )


@dataclass
class Card:
    catalog_id: str
    name: str
    category: str  # Pokemon, Trainer, Energy
    stage: str = ""
    types: list[str] = field(default_factory=list)
    hp: int = 0
    attacks: list[Attack] = field(default_factory=list)
    abilities: list[Ability] = field(default_factory=list)
    weaknesses: list[dict[str, str]] = field(default_factory=list)
    resistances: list[dict[str, str]] = field(default_factory=list)
    retreat: int = 1
    evolves_from: str | None = None
    trainer_kind: str | None = None
    energy_type: str | None = None
    image: str | None = None
    set_name: str | None = None
    text: str = ""
    dex_id: int | None = None

    @property
    def is_pokemon(self) -> bool:
        return self.category.lower() == "pokemon"

    @property
    def is_basic(self) -> bool:
        stage = (self.stage or "").lower()
        return self.is_pokemon and stage in {"basic", ""}

    @property
    def is_energy(self) -> bool:
        return self.category.lower() == "energy"

    @property
    def is_trainer(self) -> bool:
        return self.category.lower() == "trainer"

    @property
    def is_item(self) -> bool:
        return self.is_trainer and (self.trainer_kind or "").lower() in {"item", ""}

    @property
    def is_supporter(self) -> bool:
        return self.is_trainer and (self.trainer_kind or "").lower() == "supporter"

    @property
    def as_energy_type(self) -> str | None:
        if self.is_energy:
            return self.energy_type or (self.types[0] if self.types else "Colorless")
        if self.is_pokemon and self.types:
            return self.types[0]
        return None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Card:
        attacks = [Attack.from_dict(a) if isinstance(a, dict) else a for a in data.get("attacks") or []]
        abilities = [Ability.from_dict(a) if isinstance(a, dict) else a for a in data.get("abilities") or []]
        return cls(
            catalog_id=str(data.get("catalog_id") or data.get("id") or data.get("name")),
            name=data["name"],
            category=data.get("category") or data.get("supertype") or "Pokemon",
            stage=data.get("stage") or "",
            types=list(data.get("types") or []),
            hp=int(data.get("hp") or 0),
            attacks=attacks,
            abilities=abilities,
            weaknesses=list(data.get("weaknesses") or []),
            resistances=list(data.get("resistances") or []),
            retreat=int(data.get("retreat") or 0),
            evolves_from=data.get("evolves_from"),
            trainer_kind=data.get("trainer_kind"),
            energy_type=data.get("energy_type"),
            image=data.get("image"),
            set_name=data.get("set_name"),
            text=data.get("text") or "",
            dex_id=data.get("dex_id"),
        )


@dataclass
class FamilyRules:
    name: str = "Family Cup"
    deck_size: int = 30
    opening_hand: int = 7
    prize_count: int = 3
    bench_size: int = 5
    max_turns: int = 40
    pokemon_as_energy: bool = True
    any_stage_playable: bool = False
    first_player_no_attack: bool = True
    first_player_no_draw: bool = True
    first_player_no_supporter: bool = True
    first_turn_no_evolve: bool = True
    one_retreat_per_turn: bool = True
    extra_prize_for_ex: bool = True
    max_copies_except_basic_energy: int = 4
    notes: str = (
        "30 Cards 4 of a name, Pokémon = Energy: 30-card decks, 3 prize cards, and "
        "every Pokémon can be attached as a Basic Energy of its type (so Energy "
        "Search may also fetch a Pokémon). A deck may include at most 4 copies of "
        "a card with the same name, except basic Energy (unlimited). Same name "
        "includes every printing; Clefable, Clefable ex, and Mega Clefable ex are "
        "different names. Knocking Out a Pokémon ex takes 2 prize cards; Knocking "
        "Out a Mega ex takes 3. Other play follows standard Pokémon TCG: going "
        "first cannot draw, attack, or play a Supporter on the first turn; neither "
        "player may evolve on their first turn; a Pokémon cannot evolve the turn "
        "it entered play; one manual retreat per turn (Switch does not count). "
        "Opening mulligans until a Basic Pokémon; the opponent then draws one card "
        "per mulligan (always taken)."
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> FamilyRules:
        if not data:
            return default_family_rules()
        base = default_family_rules()
        for key, value in data.items():
            if hasattr(base, key) and value is not None:
                setattr(base, key, value)
        return base


def default_family_rules() -> FamilyRules:
    return FamilyRules()


def no_pokemon_energy_family_rules() -> FamilyRules:
    """30 Cards 4 of a name: Family Cup 30 / 3 prizes, Pokémon are not Basic Energy."""
    return FamilyRules(
        name="30 Cards 4 of a name",
        pokemon_as_energy=False,
        any_stage_playable=False,
        notes=(
            "30 Cards 4 of a name: 30-card decks, 3 prize cards, standard Basic Energy "
            "only (Pokémon in hand are not Basic Energy). Energy Search finds Energy "
            "cards, not Pokémon. Copy cap 4 except basic Energy. Knocking Out a "
            "Pokémon ex takes 2 prize cards; Knocking Out a Mega ex takes 3. "
            "Opening mulligans until a Basic Pokémon."
        ),
    )


def standard_30_rules() -> FamilyRules:
    """Official-style 30-card Standard: 2 of a name, Pokémon are not energy."""
    return FamilyRules(
        name="Standard 30 cards",
        deck_size=30,
        prize_count=3,
        pokemon_as_energy=False,
        any_stage_playable=False,
        max_copies_except_basic_energy=2,
        notes=(
            "Standard 30 cards: 30-card decks, 3 prize cards, at most 2 copies of a "
            "card with the same name except basic Energy (unlimited). Pokémon are not "
            "Basic Energy. Energy Search finds Energy cards, not Pokémon. Knocking Out "
            "a Pokémon ex takes 2 prize cards; Knocking Out a Mega ex takes 3."
        ),
    )


def standard_60_rules() -> FamilyRules:
    """Official Standard constructed: 60 cards, 4 of a name, 6 prizes."""
    return FamilyRules(
        name="Standard 60 cards",
        deck_size=60,
        prize_count=6,
        pokemon_as_energy=False,
        any_stage_playable=False,
        max_copies_except_basic_energy=4,
        notes=(
            "Standard 60 cards: 60-card decks, 6 prize cards, at most 4 copies of a "
            "card with the same name except basic Energy (unlimited). Pokémon are not "
            "Basic Energy. Energy Search finds Energy cards, not Pokémon. Knocking Out "
            "a Pokémon ex takes 2 prize cards; Knocking Out a Mega ex takes 3."
        ),
    )


RULE_PRESET_LABELS: dict[str, str] = {
    "b": "30 Cards 4 of a name, Pokémon = Energy",
    "c": "30 Cards 4 of a name",
    "s30": "Standard 30 cards",
    "s60": "Standard 60 cards",
}

RULE_PRESETS: dict[str, FamilyRules] = {
    "b": default_family_rules(),
    "rule_b": default_family_rules(),
    "c": no_pokemon_energy_family_rules(),
    "rule_c": no_pokemon_energy_family_rules(),
    "no_pokemon_energy": no_pokemon_energy_family_rules(),
    "s30": standard_30_rules(),
    "standard_30": standard_30_rules(),
    "s60": standard_60_rules(),
    "standard_60": standard_60_rules(),
}

CANONICAL_RULE_PRESETS = ("b", "c", "s30", "s60")


def rule_preset_label(key: str | None, fallback: str | None = None) -> str:
    canon = canonical_rule_key(key) if key else None
    if canon and canon in RULE_PRESET_LABELS:
        return RULE_PRESET_LABELS[canon]
    return fallback or (key or "")


def canonical_rule_key(raw: str | None) -> str | None:
    key = str(raw or "").lower().strip().replace("-", "_").replace("rule_", "").replace("rule ", "")
    if key in {"s30", "standard_30", "std30", "std_30"}:
        return "s30"
    if key in {"s60", "standard_60", "std60", "std_60", "standard"}:
        return "s60"
    if key in {"c", "no_pokemon_energy"}:
        return "c"
    if key in {"b"}:
        return "b"
    return None


def infer_rule_preset_from_decks(decks: list[dict | None]) -> str | None:
    """If every named deck is legal under exactly one shared preset, use that preset."""
    sets: list[set[str]] = []
    for deck in decks:
        if not deck:
            continue
        presets = normalize_rule_presets(deck.get("rule_presets"))
        if not presets:
            summary = deck.get("rule_preset")
            if summary in CANONICAL_RULE_PRESETS:
                presets = [summary]
        if presets:
            sets.append(set(presets))
    if not sets:
        return None
    common = set.intersection(*sets)
    if len(common) == 1:
        return next(iter(common))
    return None


def resolve_simulation_rules(
    *,
    rule_preset: str | None = None,
    decks: list[dict | None] | None = None,
    fallback: FamilyRules | None = None,
) -> FamilyRules:
    raw = rule_preset
    if raw not in (None, ""):
        key = canonical_rule_key(str(raw))
        if not key:
            raise ValueError("unknown rule_preset (use b, c, s30, or s60)")
        return rules_from_preset(key)
    inferred = infer_rule_preset_from_decks(list(decks or []))
    if inferred:
        return rules_from_preset(inferred)
    return fallback if fallback is not None else default_family_rules()


def normalize_rule_presets(raw: Any, fallback: list[str] | None = None) -> list[str]:
    if raw is None:
        items = list(fallback or [])
    elif isinstance(raw, str):
        items = [raw]
    elif isinstance(raw, (list, tuple, set)):
        items = list(raw)
    else:
        items = list(fallback or [])
    out: list[str] = []
    for item in items:
        key = canonical_rule_key(item if isinstance(item, str) else str(item or ""))
        if key and key not in out:
            out.append(key)
    return out


def default_rule_presets_for(deck_id: str | None) -> list[str]:
    did = str(deck_id or "")
    if did in {"seed-e", "seed-f"}:
        return ["c"]
    if did == "seed-t":
        return ["s30"]
    if did.startswith("seed-"):
        return ["b"]
    return ["b"]


def legacy_rule_presets_for(deck_id: str | None) -> list[str]:
    """Pre-column sets: seeds stay B/C/s30; household lists used to match every filter."""
    did = str(deck_id or "")
    if did in {"seed-e", "seed-f"}:
        return ["c"]
    if did == "seed-t":
        return ["s30"]
    if did.startswith("seed-"):
        return ["b"]
    return ["b", "c"]


def rule_preset_summary(presets: list[str]) -> str:
    keys = normalize_rule_presets(presets)
    if len(keys) == 1:
        return keys[0]
    return "any"


def rules_from_preset(key: str | None) -> FamilyRules:
    if not key:
        return default_family_rules()
    canon = canonical_rule_key(key) or str(key).lower().strip()
    return RULE_PRESETS.get(canon, default_family_rules())


def infer_rule_preset_from_rules(rules: FamilyRules | dict[str, Any] | None) -> str:
    """Map a rules blob to the closest selectable preset."""
    if not rules:
        return "b"
    data = rules.to_dict() if isinstance(rules, FamilyRules) else dict(rules)
    size = int(data.get("deck_size") or 0)
    copies = int(data.get("max_copies_except_basic_energy") or 0)
    prizes = int(data.get("prize_count") or 0)
    poke_energy = data.get("pokemon_as_energy")
    if size == 60 and copies == 4 and prizes == 6 and poke_energy is False:
        return "s60"
    if size == 30 and copies == 2 and prizes == 3 and poke_energy is False:
        return "s30"
    if size == 30 and copies == 4 and prizes == 3 and poke_energy is False:
        return "c"
    if poke_energy is False:
        return "c"
    return "b"
