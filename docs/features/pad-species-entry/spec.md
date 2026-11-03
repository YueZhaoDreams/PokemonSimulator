# Pad species entry

Status: done

Epic: poke-pad

Jira Issue: TBD

GitHub Issue: TBD

## Problem And Value

The device needs a Pokémon inside the screen. A search for 皮卡丘, pikachu, or 25 fills the glass with the picture and the animation, and the white half reads the number, name, type, category, height, weight, ability, and one Simplified Chinese sentence. The play triangle speaks that sentence in `zh-CN` and the cry can play.

## Scope

- `GET /api/pad/species?q=` and `GET /api/pad/species/{id}` behind the existing login.
- Source is PokéAPI with an application User-Agent and a file cache under `data/cache/pad/` (already gitignored). Do not commit a national-dex dump.
- Entry fields: id, zh-Hans name, types, category, abilities, height_m, weight_kg, flavor (newest zh-Hans line or empty), artwork URL, animation URL, cry URL, speech_text.
- Height and weight use PokéAPI units converted (decimeters → meters, hectograms → kilograms). 皮卡丘 is 0.4 and 6.0.
- speech_text is name, category, and the flavor line when present. When flavor is missing, speech_text is the Chinese attributes only. Never an English sentence and never a model-written bio.
- Unknown query is HTTP 404.
- Several prefix hits return `match: many` and a short list. One exact hit returns `match: one`.
- The Pad search box calls this API. One hit fills `#padSprite` (animation, artwork behind it) and `#padReadout`. The idle ball hides.
- `#padSpeak` speaks `speech_text` with `speechSynthesis` `lang=zh-CN` and cancels on a second press. A cry control plays `cry_url`.

## Non-Goals

- Photo match.
- Scraping 52Poké.
- Adding Perfect Order 081 as a catalog row.
- Changing card search or the engine.

## Implementation Outline

1. Add `app/pad/species.py` with an injectable transport and a name index.
2. Wire the routes in `app/main.py`.
3. Fill the device from `app.js`.
4. Test with fixtures, not the live API: 皮卡丘, pikachu, 25, unknown, and 菊草叶 with no flavor.

## Data Model And API Impact

New read-only routes. Cache files live in `data/cache/pad/`.

## Acceptance Criteria

- [x] 皮卡丘 returns id 25, type 电, category 鼠宝可梦, ability 静电, 0.4 m, 6.0 kg, a zh-Hans flavor line, artwork, animation, cry, and speech_text that includes the flavor line.
- [x] pikachu and 25 return the same id.
- [x] An unknown name is 404.
- [x] 菊草叶 has an empty flavor and speech_text without a Latin sentence.
- [x] The play control uses `zh-CN` and cancels speech when pressed again.

## Validation Plan

- Build/compile: `.venv/bin/python -m compileall -q app`
- Targeted tests: `.venv/bin/pytest -q tests/test_pad_species.py tests/test_pad_shell.py`
- Broader validation: `tests/test_ui.py`
- Manual review: search 皮卡丘 in the device at iPad landscape width.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
