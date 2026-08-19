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
    closers: list[str] = field(default_factory=list)
    prefer_chip: bool = False

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
            "closers": list(self.closers),
            "prefer_chip": self.prefer_chip,
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
    "shock": StrategySpec(
        name="shock",
        description=(
            "Set B chip line: Thunder Shock Pikachu or Electrike (damage + paralysis), "
            "keep Nuzzle Pikachu in hand as Lightning energy, bench Plusle as the closer. "
            "After about 80 damage, Plusle's Plus Damage is (damage + 10) × 2 into "
            "Dondozo's weakness and finishes the 20 HP Volt Tackle cannot."
        ),
        prefer_damage=0.7,
        prefer_status=0.9,
        bench_fill=0.0,
        evolve_asap=0.7,
        attach_pokemon_as_energy=0.95,
        item_spend=0.2,
        hold_as_energy=True,
        protect=["Pikachu", "Plusle"],
        search_aces=["Pikachu", "Electrike"],
        status_targets=["Dondozo", "Wailmer", "Orthworm"],
        backups=["Electrike"],
        insurance=["Wailmer", "Sudowoodo", "Relicanth"],
        insurance_bench=2,
        insurance_non_fuel=True,
        max_ace_copies=1,
        closers=["Plusle"],
        prefer_chip=True,
    ),
    "party": StrategySpec(
        name="party",
        description=(
            "Set C Clefairy / Mewtwo: vs glass (Set B etc.) Plan Storm — keep Clefairy "
            "Active, Moon-Watching Party for Psychic, attach until Wonder Storm ([C][C][C]) "
            "is online; 4–5 Psychic in play already KOs 60–70 HP Lightning. Save Hop when "
            "Storm can fire. Vs Ogerpon/Demolish: Plan A Transfer Charge → Mewtwo Photon "
            "(7P+Belt or 9P); Plan B Mega wall only if Mewtwo cannot eat the next 140. "
            "Never end turn on 60 HP Clefairy into Demolish. Cap Clefairy at 3."
        ),
        prefer_damage=0.95,
        prefer_status=0.1,
        bench_fill=0.0,
        evolve_asap=0.0,
        attach_pokemon_as_energy=0.95,
        item_spend=1.0,
        hold_as_energy=True,
        protect=["Clefairy", "Mewtwo ex"],
        search_aces=["Clefairy"],
        closers=["Mewtwo ex"],
        max_ace_copies=3,
    ),
    "demolish": StrategySpec(
        name="demolish",
        description=(
            "Set D Cornerstone Ogerpon: Nest Ball into Ogerpon, T1 Fighting + T2 DCE = Demolish 140. "
            "Bravery Charm to 260 HP. Acerola resets a chipped Ogerpon. Stance blocks Pokémon that have Abilities."
        ),
        prefer_damage=1.0,
        prefer_status=0.05,
        bench_fill=0.0,
        evolve_asap=0.0,
        attach_pokemon_as_energy=0.7,
        item_spend=1.0,
        hold_as_energy=True,
        protect=["Cornerstone Mask Ogerpon ex"],
        search_aces=["Cornerstone Mask Ogerpon ex"],
        max_ace_copies=1,
    ),
    "invisible": StrategySpec(
        name="invisible",
        description=(
            "Jungle Mr. Mime wall line: keep Mime Active so ≥30 after W/R is prevented."
        ),
        prefer_damage=0.95,
        prefer_status=0.1,
        bench_fill=0.0,
        evolve_asap=0.0,
        attach_pokemon_as_energy=0.95,
        item_spend=1.0,
        hold_as_energy=True,
        protect=["Mr. Mime"],
        search_aces=["Mr. Mime"],
        max_ace_copies=2,
    ),
    "crunch": StrategySpec(
        name="crunch",
        description=(
            "Orthworm vs Charm Ogerpon: Nest Ball Orthworm, Bravery Charm to 190 HP "
            "so one Demolish does not KO. Load Metal Pokémon-as-energy onto Orthworm. "
            "Hop thins toward ≤3 cards. Maximum Belt + Crunch-Time Rush (90+150+50) OHKOs "
            "260 HP Charm Ogerpon. Orthworm has no Ability, so Cornerstone Stance does not block. "
            "Cap one Orthworm in play; extras are Metal fuel."
        ),
        prefer_damage=1.0,
        prefer_status=0.05,
        bench_fill=0.0,
        evolve_asap=0.0,
        attach_pokemon_as_energy=0.95,
        item_spend=1.0,
        hold_as_energy=True,
        protect=["Orthworm"],
        search_aces=["Orthworm"],
        closers=["Orthworm"],
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
