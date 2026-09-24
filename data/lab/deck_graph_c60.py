"""Deck knowledge graph for seed deck c60 (Clefairy / Mewtwo), per combo-design.md section 3.11.

Hard edges come from the parsers only. Where the printed sentence has a link the parser
does not emit (or emits with the wrong parameters), the edge is recorded as a parser gap
with the exact printed sentence; gaps are never counted as hard edges.

Reach is a draw-only Monte Carlo, going second: opening 7 (mulligan until a Basic),
6 prizes, then one draw per turn. Seen cards by the end of our turn t = 7 + t.
One Supporter per turn; no draw Supporter is resolved. Two variants:
  parsed: searcher bases as the parser emits them today
  print:  searcher bases as the printed sentence says

Run: python3 data/lab/deck_graph_c60.py  ->  data/lab/deck-graph-c60.json
"""

from __future__ import annotations

import collections
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.effects import (
    parse_ability_effects,
    parse_effects,
    parse_energy_effects,
    parse_trainer_effects,
)

ROOT = Path(__file__).resolve().parents[2]
DECK_ID = "c60"
TRIALS = 200_000
SEED = 20260923

deck = json.loads((ROOT / "data" / "seed_decks.json").read_text())[DECK_ID]
counts: collections.Counter[str] = collections.Counter()
cards: dict[str, dict] = {}
for c in deck["cards"]:
    counts[c["catalog_id"]] += 1
    cards.setdefault(c["catalog_id"], c)
assert sum(counts.values()) == 60


def cid(name: str) -> str:
    hits = [k for k, c in cards.items() if c["name"] == name]
    assert len(hits) == 1, name
    return hits[0]


CLEFAIRY = cid("Clefairy")
MEWTWO = cid("Mewtwo ex")
CLEFABLE_EX = cid("Clefable ex")
MEGA = cid("Mega Clefable ex")
METRONOME = next(k for k, c in cards.items() if c["name"] == "Clefable" and any(a["name"] == "Metronome" for a in c["attacks"]))
PRANKISH = next(k for k, c in cards.items() if c["name"] == "Clefable" and k != METRONOME)
PSY = cid("Psychic Energy")


def parsed_effects(c: dict) -> list[dict]:
    """Every effect the shipped parsers emit for this printing, tagged with where it came from."""
    out: list[dict] = []
    text = c.get("text") or ""
    if c["category"] == "Trainer" and text:
        out += [{**e, "_parser": "parse_trainer_effects", "_on": "card"} for e in parse_trainer_effects(text)]
        kinds = {e["kind"] for e in out}
        out += [
            {**e, "_parser": "parse_effects", "_on": "card"}
            for e in parse_effects(text)
            if e["kind"] not in kinds
        ]
    if c["category"] == "Energy" and text:
        out += [{**e, "_parser": "parse_energy_effects", "_on": "card"} for e in parse_energy_effects(text)]
    for a in c.get("abilities") or []:
        t = a.get("text") or a.get("effect") or ""
        out += [{**e, "_parser": "parse_ability_effects", "_on": a["name"]} for e in parse_ability_effects(t)]
    for a in c.get("attacks") or []:
        t = a.get("text") or a.get("effect") or ""
        if t:
            out += [{**e, "_parser": "parse_effects", "_on": a["name"]} for e in parse_effects(t)]
    return out


def sentence(c: dict, on: str) -> str:
    if on == "card":
        return (c.get("text") or "").replace("\n", " ")
    for a in (c.get("abilities") or []) + (c.get("attacks") or []):
        if a["name"] == on:
            return (a.get("text") or a.get("effect") or "").replace("\n", " ")
    return ""


pokemon = [k for k, c in cards.items() if c["category"] == "Pokemon"]
basics = [k for k in pokemon if cards[k]["stage"] == "Basic"]
rule_box = {k for k in pokemon if cards[k]["name"].endswith(" ex")}
items = [k for k, c in cards.items() if c["category"] == "Trainer" and c["trainer_kind"] == "item"]
psychic_pokemon = [k for k in pokemon if "Psychic" in cards[k]["types"]]

edges: list[dict] = []


def edge(src: str, dst: str, kind: str, status: str, *, on: str, parser: str | None = None, note: str = "") -> None:
    edges.append(
        {
            "src": src,
            "dst": dst,
            "kind": kind,
            "status": status,  # parsed | parser_gap | param_gap
            "on": on,
            "parser": parser,
            "sentence": sentence(cards[src], on) if src in cards else "",
            "note": note,
        }
    )


effects_by_card = {k: parsed_effects(c) for k, c in cards.items()}

for k, c in cards.items():
    if c.get("evolves_from"):
        base = next(b for b in pokemon if cards[b]["name"] == c["evolves_from"])
        edges.append({"src": base, "dst": k, "kind": "evolves_into", "status": "parsed", "on": "evolves_from",
                      "parser": "catalog", "sentence": f"Evolves from {c['evolves_from']}", "note": ""})

for k, effs in effects_by_card.items():
    for e in effs:
        kind, on, parser = e["kind"], e["_on"], e["_parser"]
        if kind == "call_family" and "pokemon_type" in e:
            for t in basics:
                if e["pokemon_type"] in cards[t]["types"]:
                    edge(k, t, "fetches", "parsed", on=on, parser=parser)
        elif kind == "call_family":
            for t in basics:
                printed_ok = not (cards[k]["name"] == "Buddy-Buddy Poffin" and cards[t]["hp"] > 70)
                if printed_ok:
                    edge(k, t, "fetches", "parsed", on=on, parser=parser)
                else:
                    edge(k, t, "fetches", "param_gap", on=on, parser=parser,
                         note="parser drops '70 HP or less'; print excludes this target")
        elif kind == "search_pokemon_no_rule_box":
            for t in pokemon:
                if t not in rule_box:
                    edge(k, t, "fetches", "parsed", on=on, parser=parser)
        elif kind == "search_item":
            for t in items:
                edge(k, t, "fetches", "parsed", on=on, parser=parser)
        elif kind == "attach_energy_from_deck_per_benched":
            edge(k, PSY, "attaches_from_deck", "parsed", on=on, parser=parser)
            edge(k, CLEFAIRY, "scales_with_benched", "parsed", on=on, parser=parser)
        elif kind in {"psychic_energy_times", "psychic_energy_bonus"}:
            edge(k, PSY, "scales_with_in_play", "parsed", on=on, parser=parser)
        elif kind == "transfer_charge":
            edge("zone:own_discard", k, "consumes", "parsed", on=on, parser=parser)
            edges[-1]["sentence"] = sentence(cards[k], on)
        elif kind == "move_psychic_energy":
            edge(k, PSY, "moves_energy", "parsed", on=on, parser=parser)
        elif kind == "discard_hand_energy_bonus":
            edge(k, "zone:own_discard", "produces", "parsed", on=on, parser=parser)
        elif kind == "copy_active_attack":
            edge(k, "zone:opp_active", "copies_attack", "parsed", on=on, parser=parser)
        elif kind == "recycle_energy_from_discard":
            edge("zone:own_discard", k, "consumes", "param_gap", on=on, parser=parser,
                 note="parser: 2 Basic Energy; print: 1 Pokémon or 1 Basic Energy")
            edges[-1]["sentence"] = sentence(cards[k], on)
        elif kind in {"draw", "draw_until_hand"}:
            edge(k, "zone:own_deck", "draws", "parsed", on=on, parser=parser)

GAPS = [
    (cid("Ultra Ball"), "role:any_pokemon", "fetches", "card", "no parser emits a search; the kernel resolves Ultra Ball by name"),
    (cid("Ultra Ball"), "zone:own_discard", "produces", "card", "discard cost not parsed"),
    (cid("Boss's Orders"), "zone:opp_bench", "forces_active", "card", "gust not parsed for this Supporter"),
    (cid("Switch"), "zone:own_bench", "switches", "card", "not parsed"),
    (cid("Energy Switch"), PSY, "moves_energy", "card", "not parsed"),
    (cid("Maximum Belt"), "zone:opp_active", "damage_bonus_vs_ex", "card", "not parsed"),
    (cid("Battle Cage"), "zone:own_bench", "protects_bench", "card", "stadium not parsed"),
    (cid("Arven"), "role:tool", "fetches", "card", "parser keeps the Item half only"),
    (CLEFABLE_EX, PSY, "no_retreat_with", "Lunar Zone", "ability not parsed"),
    (PRANKISH, "zone:opp_active", "removes_energy", "Prankish", "ability not parsed"),
]
for src, dst, kind, on, note in GAPS:
    edge(src, dst, kind, "parser_gap", on=on, note=note)


def hard_linked(k: str) -> bool:
    """Spec isolated/junk test: any parsed link to another card or role, other than a generic draw."""
    for e in edges:
        if e["status"] != "parsed" or e["kind"] == "draws":
            continue
        if e["src"] == k and e["dst"] != k:
            return True
        if e["dst"] == k and e["src"] != k:
            return True
    return False


def draw_only(k: str) -> bool:
    return any(e["src"] == k and e["kind"] == "draws" and e["status"] == "parsed" for e in edges)


# ---- Reach Monte Carlo -------------------------------------------------------------

BASES = {
    "parsed": {
        cid("Nest Ball"): ({CLEFAIRY, MEWTWO}, 1),
        cid("Buddy-Buddy Poffin"): ({CLEFAIRY, MEWTWO}, 2),
        cid("Poké Pad"): ({CLEFAIRY, METRONOME, PRANKISH}, 1),
    },
    "print": {
        cid("Nest Ball"): ({CLEFAIRY, MEWTWO}, 1),
        cid("Buddy-Buddy Poffin"): ({CLEFAIRY}, 2),
        cid("Poké Pad"): ({CLEFAIRY, METRONOME, PRANKISH}, 1),
        cid("Ultra Ball"): (set(pokemon), 1),
    },
}
TELEPATHIC = cid("Telepathic Psychic Energy")
ARVEN = cid("Arven")

pool = [k for k, n in counts.items() for _ in range(n)]
basic_set = set(basics)


def deal(rng: random.Random) -> tuple[list[str], list[str], list[str], int]:
    mulligans = 0
    while True:
        rng.shuffle(pool)
        if any(x in basic_set for x in pool[:7]):
            break
        mulligans += 1
    opening = pool[:7]
    prizes = pool[7:13]
    rest = pool[13:]
    return opening, prizes, rest, mulligans


def fetchers(hand: collections.Counter, variant: str, target: str) -> list[tuple[str, int]]:
    out = []
    for s, (basis, cap) in BASES[variant].items():
        if target in basis:
            out += [(s, cap)] * hand[s]
    return out


def arven_item(deck_left: collections.Counter, variant: str, target: str) -> tuple[str, int] | None:
    best = None
    for s, (basis, cap) in BASES[variant].items():
        if target in basis and deck_left[s] > 0 and (best is None or cap > best[1]):
            best = (s, cap)
    return best


def trial(rng: random.Random, variant: str) -> dict[str, bool]:
    opening, prizes, rest, _ = deal(rng)
    h1 = collections.Counter(opening + rest[:1])
    h2 = collections.Counter(opening + rest[:2])
    in_deck = collections.Counter(rest[1:])
    res: dict[str, bool] = {}

    # Goal: Clefairy starts Active and at least 2 Clefairy are in play by the end of turn 1.
    clef_deck = in_deck[CLEFAIRY]
    if CLEFAIRY in opening:
        need = 2 - h1[CLEFAIRY]
        cap = sum(c for _, c in fetchers(h1, variant, CLEFAIRY))
        if h1[TELEPATHIC]:
            cap += 2
        if h1[ARVEN]:
            a = arven_item(in_deck, variant, CLEFAIRY)
            cap += a[1] if a else 0
        res["moon_party_t1"] = need <= 0 or min(cap, clef_deck) >= need
    else:
        res["moon_party_t1"] = False

    # Goal: Mewtwo ex in play by the end of turn 1.
    if h1[MEWTWO]:
        res["mewtwo_t1"] = True
    else:
        ok = bool(fetchers(h1, variant, MEWTWO))
        if not ok and h1[ARVEN]:
            ok = arven_item(in_deck, variant, MEWTWO) is not None
        res["mewtwo_t1"] = ok and in_deck[MEWTWO] > 0

    # Goals: Clefairy in play by turn 1, then a Stage 1 in hand by turn 2 to evolve it.
    for goal, target in (("clefable_ex_t2", CLEFABLE_EX), ("metronome_t2", METRONOME), ("mega_clefable_t2", MEGA)):
        best = False
        for arven_for in ("clefairy", "target"):
            spent: collections.Counter = collections.Counter()
            arven_used = False
            if h1[CLEFAIRY]:
                clef_ok = True
            else:
                fs = sorted(fetchers(h1, variant, CLEFAIRY),
                            key=lambda f: target in BASES[variant][f[0]][0])
                clef_ok = False
                if fs and in_deck[CLEFAIRY] > 0:
                    spent[fs[0][0]] += 1
                    clef_ok = True
                elif arven_for == "clefairy" and h1[ARVEN] and in_deck[CLEFAIRY] > 0:
                    clef_ok = arven_item(in_deck, variant, CLEFAIRY) is not None
                    arven_used = clef_ok
            if not clef_ok:
                continue
            if h2[target]:
                best = True
                break
            left = h2 - spent
            tgt_ok = in_deck[target] > 0 and bool(fetchers(left, variant, target))
            if not tgt_ok and not arven_used and left[ARVEN] and in_deck[target] > 0:
                tgt_ok = arven_item(in_deck, variant, target) is not None
            if tgt_ok:
                best = True
                break
        res[goal] = best
    res["any_stage1_t2"] = res["clefable_ex_t2"] or res["metronome_t2"] or res["mega_clefable_t2"]
    res["attacker_t2"] = res["mewtwo_t1"] or res["any_stage1_t2"]
    return res


def nodes_label(k: str) -> str:
    return cards[k]["name"] + (" (Metronome)" if k == METRONOME else " (Prankish)" if k == PRANKISH else "")


def mulligan_rate(rng: random.Random, n: int) -> float:
    basics_n = sum(counts[b] for b in basics)
    hits = 0
    for _ in range(n):
        hand = rng.sample(range(60), 7)
        if not any(i < basics_n for i in hand):
            hits += 1
    return hits / n


def measure(variant: str, trials: int, removed: str | tuple[str, ...] | None = None) -> dict[str, float]:
    global pool
    gone = set(removed if isinstance(removed, tuple) else (removed,) if removed else ())
    full = [k for k, n in counts.items() for _ in range(n)]
    pool = ["blank" if k in gone else k for k in full]
    rng = random.Random(SEED)
    tally: collections.Counter[str] = collections.Counter()
    for _ in range(trials):
        for g, ok in trial(rng, variant).items():
            tally[g] += ok
    pool = full
    return {g: round(v / trials, 4) for g, v in tally.items()}


REMOVAL_TRIALS = 60_000


def run() -> dict:
    reach = {variant: measure(variant, TRIALS) for variant in ("parsed", "print")}

    # Remove every copy of one name (replaced by a blank card) and re-measure, print variant.
    base = measure("print", REMOVAL_TRIALS)
    removal = {}
    for k in cards:
        if k == PSY:
            continue
        r = measure("print", REMOVAL_TRIALS, removed=k)
        removal[k] = {g: round(r[g] - base[g], 4) for g in base}
    assert set(basics) == {CLEFAIRY, MEWTWO}
    cut_pair = {"removed": ["Clefairy", "Mewtwo ex"], "attacker_t2": 0.0,
                "note": "no Basic Pokémon left, so no legal opening hand; the smallest cut of attacker_t2 is these two names"}

    prized_all = {}
    for k, n in counts.items():
        if n <= 6:
            prized_all[cards[k]["name"] + (" (Metronome)" if k == METRONOME else " (Prankish)" if k == PRANKISH else "")] = round(
                math.comb(60 - n, 6 - n) / math.comb(60, 6), 4)

    nodes = []
    for k, c in cards.items():
        label = c["name"] + (" (Metronome)" if k == METRONOME else " (Prankish)" if k == PRANKISH else "")
        nodes.append({
            "id": k,
            "label": label,
            "type": "printing",
            "category": c["category"],
            "stage": c["stage"],
            "hp": c["hp"],
            "types": c["types"],
            "copies": counts[k],
            "hard_linked": hard_linked(k),
            "draw_only": draw_only(k) and not hard_linked(k),
            "parser_gap": any(e["src"] == k and e["status"] != "parsed" for e in edges),
        })
    for z in ("zone:own_discard", "zone:own_deck", "zone:own_bench", "zone:opp_active", "zone:opp_bench",
              "role:any_pokemon", "role:tool"):
        nodes.append({"id": z, "label": z.split(":", 1)[1], "type": z.split(":", 1)[0]})

    return {
        "deck": DECK_ID,
        "deck_name": deck["name"],
        "trials": TRIALS,
        "seed": SEED,
        "assumptions": "going second; opening 7 with mulligan until a Basic; 6 prizes; one draw per turn; "
                       "one Supporter per turn; no draw Supporter resolved; Telepathic needs a Psychic Pokémon in play",
        "basics": {cards[b]["name"]: counts[b] for b in basics},
        "mulligan_rate": round(mulligan_rate(random.Random(SEED), TRIALS), 4),
        "p_all_copies_prized": prized_all,
        "reach": reach,
        "removal_trials": REMOVAL_TRIALS,
        "removal_base": base,
        "removal_delta": {nodes_label(k): v for k, v in removal.items()},
        "cut_pair": cut_pair,
        "nodes": nodes,
        "edges": edges,
    }


if __name__ == "__main__":
    out = run()
    path = ROOT / "data" / "lab" / "deck-graph-c60.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps({k: out[k] for k in ("basics", "mulligan_rate", "reach", "p_all_copies_prized")}, indent=1))
    print("removal base", out["removal_base"])
    for name, d in sorted(out["removal_delta"].items(), key=lambda kv: min(kv[1].values())):
        print(f"  {name:28s}", {g: v for g, v in d.items()})
    print("edges", collections.Counter(e["status"] for e in out["edges"]))
    print("isolated (no parsed link):", [n["label"] for n in out["nodes"] if n["type"] == "printing" and not n["hard_linked"]])
