# Combo Cub

Phone-friendly web app for a household Pokémon TCG format. Photograph a set of cards, ask questions, simulate thousands of games, and record what the AI tried and learned.

Public name **Combo Cub** (招式小熊); domain **combocub.com**. Brand notes: [docs/combo-cub.md](docs/combo-cub.md).

This is a fan-made simulator. It is not affiliated with Nintendo, Game Freak, or The Pokémon Company.

## Family Cup rules (defaults)

- **30-card** decks (play whatever you scanned; 30 is the target)
- Opening hand of **7**
- **3 prize cards**
- **Pokémon ex = 2 prizes; Mega ex = 3 prizes**
- **Rule B:** Any Pokémon can be attached as a Basic Energy of its type
- **No Pokémon energy (Rule C, selectable):** same 30 / 3-prize Family Cup, but Pokémon are **not** Basic Energy. Energy Search finds Energy only.
- Otherwise: standard Pokémon TCG turn structure (mulligans until a Basic, opponent draws one per mulligan, bench of 5, one energy attach per turn, first player does not draw or attack on turn 1)

Rule presets are available in the Fight tab and via `GET /api/rule-presets`. Existing Rule B decks stay selectable. Carpet Sets E and F are the new 30-card lists.

Rules are also editable in the API (`PUT /api/rules`).

## What it does

1. **Scan** a floor photo of a card set (iPhone HEIC works). Sample photos from this repo are auto-recognized.
2. **Look up** card data via [TCGdex](https://tcgdex.dev/) (free, no key). Optional Grok / OpenAI / Claude vision for new photos.
3. **Ask Cursor** — tap the Combo Cub mark (bottom-right). Chat opens as a split agent panel (right on desktop, top on a phone). On a computer there is no Talk/voice control; type instead. The agent can run simulations, pytest, and lab scripts, and it can edit the app when you ask.
4. **Simulate 10,000 games** with named strategies. Every run is stored in the **Lab**: method, strategy, results, sample game logs, and learning notes (which cards mattered, status rates, prize bricks).

## Reused vs built here

Searched before writing a new engine:

| Project | Why it was not vendored |
| --- | --- |
| [TCGdex API](https://tcgdex.dev/) | **Used** for card names, HP, attacks, images |
| [pokemontcg.io](https://docs.pokemontcg.io/) | Optional; needs a key for heavy use |
| [prateekt/pokemon-card-recognizer](https://github.com/prateekt/pokemon-card-recognizer) | Heavy GPU OCR stack |
| [HanClinto/CollectorVision](https://github.com/HanClinto/CollectorVision) | AGPL; Pokémon catalog is experimental |
| [bcollazo/deckgym-core](https://github.com/bcollazo/deckgym-core) | Pokémon TCG **Pocket**, not the paper game, no family energy rule |

The match engine, family rules, Monte Carlo lab, and trade search are original.

## Run on this machine

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x run.sh
./run.sh
```

Open http://127.0.0.1:8000 on the computer, or `http://<your-lan-ip>:8000` on a phone on the same Wi-Fi. Add to Home Screen for a standalone app.

Sign in with email. The household admin account is `dancedfire@gmail.com` (password from `ADMIN_PASSWORD`, default `1013`). Every existing / seeded card set is owned by that admin. New trainers register their own email and only see sets they save.

Chat is Cursor, defaulting to **Grok 4.6 Extra High**. Mint a key at [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations) and put it in `.env`. Without `CURSOR_API_KEY`, the **local coach** still answers the example questions by calling the same simulator tools.

```bash
cp .env.example .env
# CURSOR_API_KEY is the chat agent (required for "talk to Cursor")
# optional: XAI_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY for photo vision only
```

## Cursor cloud / Docker

```bash
docker build -t family-cup .
docker run --rm -p 8000:8000 --env-file .env family-cup
```

## Example questions

- What is the probability Dondozo appears in the first 7 cards?
- If I use Pikachu (Thunder Shock) to paralyze Dondozo, how often can I actually use that?
- Run 10,000 games. What strategy was used, what was the result, what did the AI learn?
- If we trade cards between the two groups, which swap makes **both** sets stronger?

## Tests

```bash
.venv/bin/pytest -q
```
