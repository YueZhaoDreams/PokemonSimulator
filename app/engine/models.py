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
        return cls(
            name=data.get("name", "Attack"),
            cost=list(data.get("cost") or ["Colorless"]),
            damage=int(data.get("damage") or 0),
            text=data.get("text") or data.get("effect") or "",
            effects=list(data.get("effects") or []),
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
        return cls(
            name=data.get("name", "Ability"),
            text=data.get("text") or data.get("effect") or "",
            effects=list(data.get("effects") or []),
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
    first_player_no_attack: bool = True
    first_player_no_draw: bool = True
    first_player_no_supporter: bool = True
    first_turn_no_evolve: bool = True
    one_retreat_per_turn: bool = True
    extra_prize_for_ex: bool = True
    max_copies_except_basic_energy: int = 4
    notes: str = (
        "30-card decks, 3 prize cards, and every Pokémon can be attached as a "
        "Basic Energy of its type (so Energy Search may also fetch a Pokémon). "
        "A deck may include at most 4 copies of a card with the same name, except "
        "basic Energy (unlimited). Same name includes every printing; Clefable, "
        "Clefable ex, and Mega Clefable ex are different names. Knocking Out a "
        "Pokémon ex takes 2 prize cards; Knocking Out a Mega ex takes 3. Other "
        "play follows standard Pokémon TCG: going first cannot draw, attack, or "
        "play a Supporter on the first turn; neither player may evolve on their "
        "first turn; a Pokémon cannot evolve the turn it entered play; one manual "
        "retreat per turn (Switch does not count). Opening mulligans until a Basic "
        "Pokémon; the opponent then draws one card per mulligan (always taken)."
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
