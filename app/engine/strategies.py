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
            "Set A family play: Dondozo is still the Hydro Splash attacker. Play one Starly "
            "and evolve Staravia → Staraptor. Boomerang Energy pays Colorless and returns "
            "after Power Blast discards it. Tailspin Away prevents damage from Basic Pokémon "
            "(Pikachu, Ogerpon, Mewtwo). Water / Metal Basics stay in hand as energy. After "
            "Dondozo is out, bench Orthworm so a single KO does not end the game. Swallow-Up "
            "looks at 3; balls hunt Dondozo."
        ),
        prefer_damage=0.85,
        prefer_status=0.2,
        bench_fill=0.0,
        evolve_asap=1.0,
        attach_pokemon_as_energy=0.9,
        item_spend=0.2,
        swallow_look=3,
        hold_as_energy=True,
        protect=["Dondozo", "Starly", "Staravia", "Staraptor"],
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
            "Set B Walrein + chip: play one Spheal, evolve Sealeo → Walrein. Water Energy "
            "and Water Basics pay Megaton Fall [W][W] 170, which KOs 160 HP Dondozo. "
            "Frigid Fangs 60 locks Pokémon with 2 or less Energy. Thunder Shock Pikachu "
            "or Electrike chip + paralyze while the line evolves; Nuzzle Pikachu stays "
            "as Lightning energy. Bench Plusle as the leftover closer. One Roselia for "
            "Soothing Scent. Play Energy Search / Retrieval / Trekking Shoes. Two "
            "Fighting sponges so Hydro Splash cannot wipe the board."
        ),
        prefer_damage=0.85,
        prefer_status=0.9,
        bench_fill=0.0,
        evolve_asap=1.0,
        attach_pokemon_as_energy=0.95,
        item_spend=1.0,
        hold_as_energy=True,
        protect=["Pikachu", "Plusle", "Roselia", "Spheal", "Sealeo", "Walrein"],
        search_aces=["Pikachu", "Electrike"],
        status_targets=["Dondozo", "Wailmer", "Orthworm"],
        backups=["Electrike"],
        insurance=["Sudowoodo", "Relicanth", "Wailmer"],
        insurance_bench=2,
        insurance_non_fuel=True,
        max_ace_copies=1,
        closers=["Plusle"],
        prefer_chip=True,
    ),
    "party": StrategySpec(
        name="party",
        description=(
            "Set C Clefairy / Mewtwo: vs A/B open on Mewtwo and keep Clefairy mostly as Psychic "
            "Energy (cap 1 vs thrifty, 0 vs shock — Hydro Splash / Thunder Shock prize 60 HP "
            "engines into deck-out). Vs D: Party ramp (cap 3) → Transfer Charge → Photon "
            "(7P+Belt or 9P); Mega wall only if Mewtwo cannot eat the next 140. "
            "151 Invitation Clefairy (if mixed in) dumps Party engines in one attack when "
            "there is no Switch to rotate Party. One Boss's Orders to pull a prize. "
            "Trainer order: hunt Maximum Belt (Arven before Tool Box), then Hop or "
            "Lillie (until 6, or 8 on your first turn), then Energy Search / Nest Ball. "
            "If Shooting Moons can KO (hand Energy discards, "
            "not vs Cornerstone Stance), evolve Mega Clefable ex instead of waiting on Photon."
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
    "slash": StrategySpec(
        name="slash",
        description=(
            "Set S Grass hunter vs Charm Ogerpon: Nest Wo-Chien ex as the 230 HP Grass "
            "Demolish sponge (no Ability, so Stance does not block). Evolve Sprigatito → "
            "Floragato. Slashing Claw 90 + Maximum Belt 50 = 140, Grass Weakness ×2 = 280 "
            "OHKO. Forest Blast 220 ×2 = 440 is the backup KO. Never end on 60/90 HP into "
            "Demolish — stay on Wo-Chien until a Grass attack KOs this turn. Cap one "
            "Sprigatito and one Wo-Chien in play; extras are Grass energy. ACE SPEC Belt "
            "on Floragato only. Paradox Rift Mewtwo is Lightning and cannot pay Photon here."
        ),
        prefer_damage=1.0,
        prefer_status=0.05,
        bench_fill=0.0,
        evolve_asap=1.0,
        attach_pokemon_as_energy=0.95,
        item_spend=1.0,
        hold_as_energy=True,
        protect=["Wo-Chien ex", "Sprigatito", "Floragato"],
        search_aces=["Wo-Chien ex"],
        closers=["Floragato"],
        backups=["Sprigatito"],
        insurance=["Wo-Chien ex"],
        insurance_bench=1,
        max_ace_copies=1,
    ),
    "phantom": StrategySpec(
        name="phantom",
        description=(
            "Set T Dragapult ex half-deck: Poffin Dreepy (and Budew). Evolve "
            "Drakloak for Recon Directive (look top N from printed text), Rare Candy "
            "to Dragapult ex. Fire + Psychic pay Phantom Dive 200 plus 6 bench "
            "counters. Budew Itchy Pollen locks Items. Fezandipiti Flip the Script "
            "draws after a KO. Do not spend the line as Family Cup energy."
        ),
        prefer_damage=1.0,
        prefer_status=0.15,
        bench_fill=0.0,
        evolve_asap=1.0,
        attach_pokemon_as_energy=0.2,
        item_spend=1.0,
        hold_as_energy=True,
        protect=["Dreepy", "Drakloak", "Dragapult ex", "Fezandipiti ex", "Budew"],
        search_aces=["Dreepy"],
        closers=["Dragapult ex"],
        backups=["Budew"],
        insurance=["Fezandipiti ex"],
        insurance_bench=1,
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
