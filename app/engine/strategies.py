from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.engine.models import Card


@dataclass
class StrategySpec:
    name: str
    description: str
    prefer_damage: float = 0.7
    prefer_status: float = 0.3
    bench_fill: float = 0.7
    evolve_asap: float = 0.9
    attach_pokemon_as_energy: float = 0.65
    item_spend: float = 1.0
    swallow_look: int | None = None
    hold_as_energy: bool = False
    protect: list[str] = field(default_factory=list)
    search_aces: list[str] = field(default_factory=list)
    status_targets: list[str] = field(default_factory=list)
    backups: list[str] = field(default_factory=list)
    insurance: list[str] = field(default_factory=list)
    insurance_bench: int = 0
    insurance_non_fuel: bool = False
    max_ace_copies: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "prefer_damage": self.prefer_damage,
            "prefer_status": self.prefer_status,
            "bench_fill": self.bench_fill,
            "evolve_asap": self.evolve_asap,
            "attach_pokemon_as_energy": self.attach_pokemon_as_energy,
            "item_spend": self.item_spend,
            "swallow_look": self.swallow_look,
            "hold_as_energy": self.hold_as_energy,
            "protect": list(self.protect),
            "search_aces": list(self.search_aces),
            "status_targets": list(self.status_targets),
            "backups": list(self.backups),
            "insurance": list(self.insurance),
            "insurance_bench": self.insurance_bench,
            "insurance_non_fuel": self.insurance_non_fuel,
            "max_ace_copies": self.max_ace_copies,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | str | None) -> StrategySpec:
        if data is None:
            return STRATEGY_LIBRARY["balanced"]
        if isinstance(data, str):
            return STRATEGY_LIBRARY.get(data.lower(), STRATEGY_LIBRARY["balanced"])
        name = (data.get("name") or "custom").lower()
        base = STRATEGY_LIBRARY.get(name, STRATEGY_LIBRARY["balanced"])
        merged = base.to_dict()
        merged.update({k: v for k, v in data.items() if v is not None})
        merged["name"] = data.get("name") or base.name
        return cls(**{k: merged[k] for k in cls.__dataclass_fields__})


STRATEGY_LIBRARY = {
    "aggressive": StrategySpec(
        name="aggressive",
        description="Evolve and attach energy to the Active Pokémon, then hit the hardest attack available.",
        prefer_damage=1.0,
        prefer_status=0.15,
        bench_fill=0.45,
        evolve_asap=1.0,
        attach_pokemon_as_energy=0.8,
    ),
    "setup": StrategySpec(
        name="setup",
        description="Fill the bench, evolve, and only attack once an attacker is powered.",
        prefer_damage=0.55,
        prefer_status=0.2,
        bench_fill=1.0,
        evolve_asap=0.85,
        attach_pokemon_as_energy=0.45,
    ),
    "control": StrategySpec(
        name="control",
        description="Prioritize Paralysis, Poison, and Burn. Use Pikachu-style status attacks when the target is a wall.",
        prefer_damage=0.35,
        prefer_status=1.0,
        bench_fill=0.6,
        evolve_asap=0.7,
        attach_pokemon_as_energy=0.7,
        status_targets=["Dondozo", "Wailmer", "Tinkaton", "Tsareena"],
        protect=["Pikachu"],
    ),
    "balanced": StrategySpec(
        name="balanced",
        description="Mix setup, energy, and damage. Protect key attackers from being spent as energy.",
        prefer_damage=0.7,
        prefer_status=0.4,
        bench_fill=0.7,
        evolve_asap=0.85,
        attach_pokemon_as_energy=0.6,
        item_spend=1.0,
    ),
    "thrifty": StrategySpec(
        name="thrifty",
        description=(
            "Set A family play: Dondozo is the attacker. Keep Water Basics in hand as "
            "energy. After Dondozo is out, bench one non-Water Pokémon (Orthworm first) "
            "so a single KO does not end the game. Swallow-Up looks at 3; balls only hunt Dondozo."
        ),
        prefer_damage=0.85,
        prefer_status=0.2,
        bench_fill=0.0,
        evolve_asap=0.85,
        attach_pokemon_as_energy=0.9,
        item_spend=0.2,
        swallow_look=3,
        hold_as_energy=True,
        protect=["Dondozo"],
        search_aces=["Dondozo"],
        backups=["Orthworm", "Flutter Mane"],
        insurance=["Orthworm"],
        insurance_bench=1,
        insurance_non_fuel=True,
        max_ace_copies=1,
    ),
    "nuzzle": StrategySpec(
        name="nuzzle",
        description=(
            "Set B family play: one Pikachu in play (prefer Volt Tackle). Lightning "
            "Basics stay in hand as energy. Nuzzle or Thunder Shock while charging, "
            "then Volt Tackle into Dondozo's Lightning weakness. Bench two non-Lightning "
            "Pokémon (Wailmer first) so Hydro Splash cannot wipe the board. Call for "
            "Family only fetches Pikachu."
        ),
        prefer_damage=0.85,
        prefer_status=0.7,
        bench_fill=0.0,
        evolve_asap=0.7,
        attach_pokemon_as_energy=0.95,
        item_spend=0.2,
        hold_as_energy=True,
        protect=["Pikachu"],
        search_aces=["Pikachu"],
        status_targets=["Dondozo", "Wailmer", "Orthworm"],
        backups=["Electrike"],
        insurance=["Wailmer", "Sudowoodo", "Relicanth"],
        insurance_bench=2,
        insurance_non_fuel=True,
        max_ace_copies=1,
    ),
}


def list_strategies() -> list[dict[str, Any]]:
    return [s.to_dict() for s in STRATEGY_LIBRARY.values()]


def protect_defaults(cards: list[Card]) -> list[str]:
    names = []
    for card in cards:
        if not card.is_pokemon:
            continue
        if (card.hp or 0) >= 140 or (card.stage or "").lower() == "stage2":
            names.append(card.name)
        if any("paralyze" in (atk.text or "").lower() for atk in card.attacks):
            names.append(card.name)
    return list(dict.fromkeys(names))
