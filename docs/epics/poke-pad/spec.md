# Pad

Status: in_delivery

GitHub Issue: TBD

## Problem And Value

The Cards tab is a catalog tool: search a card, scan a card photo, see owned copies, add one to a set. The kid will open this as a webpage on the household iPad. They want that screen to feel like the Poké Pad from the card: look up a Pokémon, see it, hear a short introduction, and still be able to look up a card. Closer to that card is the point. A correct form that does not look like the device fails.

This epic turns the Cards destination into **Pad**. Pad has two modes on one page. Card mode keeps today's card search, card photo, owned copies, and add-to-set path. Pokémon mode looks up a species. A photo of a toy or of an animated picture can start that lookup.

The screen is the handheld drawn on the Poké Pad card: red upper shell, white lower shell, a screen, and a play triangle. The reference printing is [Perfect Order 081/088](https://www.tcgplayer.com/product/684332/pokemon-me03-perfect-order-poke-pad-081-088) (TCGplayer 684332, TCGdex `me03-081`, illustrator Studio Bora Inc.). The repo already stores that same art and the same effect as Ascended Heroes 198/217 (`me02.5-198`). On the iPad, a kid should recognize that device without being told. Likeness is the bar: proportions, colors, the screen, the ball and pulse, and the play triangle. A flat red-and-white box fails. The [52Poké page for 皮卡丘](https://wiki.52poke.com/zh-hans/%E7%9A%AE%E5%8D%A1%E4%B8%98) is only the field checklist (name, number, type, category, height, weight, ability, short intro). It is not the layout and not the data source.

## Scope

Pad replaces the visible Cards screen. The bottom nav and the screen title say **Pad**. Other tabs (Sets, Fight, Lab, Combo Cub) stay as they are. Sets → Add a card / Replace a card still opens card search and can add or replace a card. A Pokémon photo never starts a new set. A card photo never opens a species entry.

### Modes

- Pad opens in **Pokémon** mode. Human edit before approval if it should open in Card mode instead.
- A toggle switches **Card** and **Pokémon**. The toggle is a control on the device, visible on the iPad without scrolling.
- Card mode still searches the existing catalog (name query, scan photo, owned copies, card detail, add to set). Matching rules and TCGdex art stay. This epic does not restyle Fight or the set editor.

### The Poké Pad device

The kid uses the household iPad, in Safari, as a normal webpage. Landscape is the view that must feel like the card: one big device on the blue field with the soft rings from the illustration, the same pose as the art. Portrait keeps that same device, scaled, and does not turn it into a form. Safari's own toolbar stays. The gate does not depend on Add to Home Screen.

The page is that handheld. It is not a wiki article, not an infobox, not a scan of the Trainer card (no Item / TRAINER header, no rules text, no 081/088), and not the current Cards form with species fields added underneath.

Draw the device so the iPad and the real card read as the same toy. Do not paste the Studio Bora illustration, or the TCGdex scan, as the page. Match the art's proportions: wide body, large inset screen, play triangle sitting on the left where the red shell meets the white shell.

- **Shell.** Red upper half, white lower half, silver rim, the same split as the card art. Shading can follow the art. A flat fill fails the likeness bar.
- **Screen.** The inset window on the red half, with the pale green-yellow glass from the art. Idle, before a result: a green ball with a small light center and a pulse line through it, as on the card. After a hit: the Pokémon picture is the largest thing in that window, and the looping animation plays there. The idle ball returns when the search is cleared.
- **Play triangle.** The triangle button on the lower left of the shell, where the card draws it. Large enough for a finger on an iPad. That button is 朗读. The cry control sits next to it. A second tap stops speech.
- **White half.** Search slot, Card / Pokémon toggle, and the readout: national number, name, type badge, category, height, weight, ability, and the one intro sentence. Short rows, readable from a kid's distance on the iPad. While 朗读 speaks, the intro sentence is the line being read. The iPad keyboard must not cover the play triangle.

Before a species is open, matches are a short list on the white half (picture, number, name). Tapping one fills the screen. Card mode uses the same device; the screen shows the TCG image and the white half shows the catalog name. Add to set stays available from there. The old finder form (a labeled input, a scan button, and a tile grid) is not the page.

This epic does not add a Perfect Order row. `PREFERRED_IDS["Poké Pad"]` stays `me02.5-198`. Same name, same printed effect, same device art.

### Pokémon lookup

- Text search accepts a Simplified Chinese name (`皮卡丘`), an English name (`pikachu`), or a national number (`25`).
- One chosen species opens an entry. Ambiguous text shows a short list first. An unknown name says it was not found and does not invent a species.
- The entry shows, in Simplified Chinese when PokéAPI has the string:
  - national number, name, type(s), category (the `鼠宝可梦` genus line), ability names, height in meters, weight in kilograms
  - one still picture (official artwork) and one looping animation (the Showdown GIF PokéAPI already hosts)
  - one short intro sentence: the newest Simplified Chinese Pokédex line on that species
  - a **朗读** button that speaks the intro in Simplified Chinese: name, category, then that sentence
  - the species cry from the same Pokémon record, played as part of the intro or from a control next to 朗读
- 朗读 uses the browser's own speech synthesis (`zh-CN`). No paid voice service. Tapping again stops speech. If that species has no Simplified Chinese Pokédex line, the entry still shows the attributes it does have, and 朗读 reads those attributes only. The app does not fill the gap with English, with a model-written bio, or with wiki prose.
- Height and weight use PokéAPI units converted for display (decimeters → meters, hectograms → kilograms). 皮卡丘 is 0.4 m and 6.0 kg.

### Photo lookup

- Pokémon mode accepts a photo. The picture may be a toy (plush or figure) or an animated / cartoon depiction of a Pokémon.
- The match is against Pad's own pictures (official artwork and the animated sprite), not a web image search and not a paid vision API.
- A confident hit opens the same entry as text search. A weak hit shows a few suggestions. No match says so. A wrong confident intro is a failure.
- Card mode keeps the current scan: a photo of cards can still name cards and start a set. That path stays on the card finder.

### Data source

Use **[PokéAPI](https://pokeapi.co/docs/v2)** (`https://pokeapi.co/api/v2`, no key). Checked against live data on 2026-11-03:

| Need | PokéAPI field | 皮卡丘 check |
| --- | --- | --- |
| Simplified name | `pokemon-species` `names` where `language.name` is `zh-hans` | 皮卡丘 |
| Category | `genera` `zh-hans` | 鼠宝可梦 |
| Intro line | `flavor_text_entries` `zh-hans` (newest version present) | present through Sword / Shield; not Scarlet / Violet |
| Type, ability | `pokemon` types and abilities, then `type` / `ability` `names` `zh-hans` | 电, 静电 |
| Height, weight | `pokemon` `height`, `weight` | 4 → 0.4 m, 60 → 6.0 kg |
| Still picture | `sprites.other.official-artwork.front_default` | hosted PNG |
| Animation | `sprites.other.showdown.front_default` | hosted GIF |
| Cry | `cries.latest` | hosted OGG |

A stride sample of 41 species (every 25th id from 1 through 1025) had a Simplified Chinese name and genus on all 41, and a Simplified Chinese flavor line on 29. Names exist for later species such as 新叶喵; many flavor lines do not (菊草叶, 洛奇亚, 新叶喵, 桃歹郎). Pad tells the truth about that gap.

The server calls PokéAPI with an application User-Agent (a bare client gets HTTP 403) and caches species payloads so repeat lookups do not hammer the public API. Card data stays on the existing catalog.

52Poké's original text is CC BY-NC-SA 3.0, its images are not licensed to this app, and its machine-reading rules forbid using the wiki as a live backend.

## Non-Goals

- Scraping or mirroring 52Poké, Bulbapedia, or Wikipedia, including their article text and images.
- A hosted catalog of toy product photos, or a general web image search.
- A paid vision API or a paid text-to-speech service.
- Inventing Pokédex prose when PokéAPI has no Simplified Chinese line.
- Every form, costume, regional variant, and Gigantamax as its own entry. Search lands on the default species unless a later epic says otherwise.
- Evolution chains, level-up move lists, episode guides, base stats as a competitive sheet, or a catch / completion tracker.
- Offline copy of the full national dex in git.
- Changes to Fight, Lab, the match engine, printed-card parsing, or deck rules.
- Replacing TCGdex as the card catalog.
- A wiki page, an infobox, a scan of the Poké Pad Trainer card, or the current Cards finder with species data added under it. The page is the handheld described above.
- Pasting the Studio Bora illustration or a TCGdex scan in as the page background.

## Acceptance Gates

Define where acceptance must be verified before dispatch continues or the epic can close. Tag each gate with **consumer** (who experiences the output) and **verifier** (who may sign off).

- **consumer:** `human` (UI/UX), `agent` (API/dispatch consumers), or `both`
- **verifier:** `agent-auto`, `agent-then-human`, or `human-required`

Operator set every verifier to `agent-auto` on 2026-11-03 and asked delivery to proceed. The iPad look in Scope still holds. These checks are what the agent runs instead of waiting for a person.

Child slices: `pad-device-shell`, `pad-species-entry`, `pad-photo-match`.

### Milestone: `pad-shows-pikachu`

- **After features:** `pad-device-shell`, `pad-species-entry`, `pad-photo-match`
- **Consumer:** `both`
- **Verifier:** `agent-auto`
- **Verify:**
  - `.venv/bin/pytest -q tests/test_pad_shell.py tests/test_pad_species.py tests/test_ui.py` passes.
  - The served HTML nav and `#view-cards` title say Pad. `data-view` values `cards`, `decks`, `fight`, and `lab` are still present. `#padDevice` starts at `data-mode="pokemon"` and contains a play control whose accessible name is 朗读.
  - `styles.css` has a landscape rule for `.pad-device`, a red upper shell, a white lower shell, and a screen idle state (ball and pulse). It does not include the strings `TRAINER` or `081/088` as the page chrome.
  - `GET /api/pad/species?q=皮卡丘` returns one entry: id 25, name 皮卡丘, a type 电, category 鼠宝可梦, an ability 静电, height_m 0.4, weight_kg 6.0, a non-empty zh-Hans flavor line, artwork URL, animation URL, cry URL, and `speech_text` containing 皮卡丘 and 鼠宝可梦 and that flavor line.
  - `q=pikachu` and `q=25` return the same id. An unknown query returns HTTP 404 and no invented flavor.
  - Species 152 (菊草叶) returns a name and category, an empty flavor, and `speech_text` that contains 菊草叶 and does not contain a Latin Pokédex sentence.
  - `app.js` starts `speechSynthesis` from `#padSpeak` with `lang` `zh-CN` and cancels speech on a second press. The cry URL is assigned to an audio element from that entry.
  - `#findPanel`, `#addName`, `#findScan`, and `#ownedGrid` remain inside `#view-cards`. `parkCardsPanel` is still the function that moves the finder. Card mode is `#padDevice[data-mode="card"]` showing `#cardsHost`.
- **Blocks dispatch until passed:** yes

### Milestone: `pad-finds-from-photo`

- **After features:** `pad-photo-match`
- **Consumer:** `agent`
- **Verifier:** `agent-auto`
- **Verify:**
  - `.venv/bin/pytest -q tests/test_pad_photo.py` passes.
  - Posting an image whose dHash matches the cached official artwork of species 25 returns that entry (`match` `one`, id 25).
  - Two close hashes and no clear winner return `match` `many` and a list that includes the right id. A distant hash returns `match` `none` and no entry name.
  - `POST /api/pad/photo` does not create a deck and does not call the card recognizer. `#findScan` still submits card photos through the existing recognize path, not `/api/pad/photo`.
- **Blocks dispatch until passed:** yes

### Epic exit

- **After features:** all child features done
- **Consumer:** `both`
- **Verifier:** `agent-auto`
- **Verify:**
  - `.venv/bin/pytest -q tests/test_pad_shell.py tests/test_pad_species.py tests/test_pad_photo.py tests/test_ui.py` passes.
  - `git diff --name-only` against the epic base does not include `app/engine/game.py` or `app/engine/effects.py` for this epic's Pad slices.
  - The Pad page still has one device, Pokémon search, 朗读, card mode, and photo match, as locked by the tests above.
- **Blocks epic `done`:** yes

## Epic Validation

- PokéAPI is the source of truth for species fields. 52Poké is a field checklist only. Do not copy its sentences or its page layout into the app, the tests, or this repo. The layout to match is the Poké Pad handheld in this spec, on an iPad-sized landscape viewport. Closer is better. The agent-auto gates lock that structure in HTML, CSS, and API tests.
- The catalog already has Poké Pad. Do not treat a missing `me03-081` row as a hole in this epic.
- Portrait must still be the same device. A page that stacks the old Cards finder fails `tests/test_pad_shell.py`.
- Flavor coverage is uneven. Tests that require a specific intro sentence must use a species known to have `zh-hans` flavor text (皮卡丘) and must compare against the API, not against a hand-written paragraph in git.
- Missing flavor text is an empty intro, not a translation task and not a scrape of another wiki.
- Speech uses iPad Safari's own Chinese voice when the play triangle is tapped (`speechSynthesis`, `zh-CN`). The agent-auto check is the utterance text and the `zh-CN` call, not a recording from the household iPad. Do not fall back to an English sentence.
- Photo matching against official art will do better on a clear cartoon still than on a plush in a messy room. The gate allows a suggestion list. It does not allow a single wrong answer stated as fact.
- Cache PokéAPI responses and send a descriptive User-Agent. Do not vendor the national dex into git for this epic.
- Card mode and the set picker share one find panel today (`parkCardsPanel`). Pokémon mode must not break that handoff.
- This epic does not change `parse_effects` or `parse_ability_effects`.

## Status Update Checklist

When the epic changes state, update the linked tracker with:

- current epic state,
- gate pass/fail notes,
- child feature progress summary,
- blockers,
- next human or agent action.
