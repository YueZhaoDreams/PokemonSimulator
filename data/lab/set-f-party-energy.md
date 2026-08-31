# Carpet Set F — Party vs energy retunes (Rule C)

Rule C: Pokémon are **not** Basic Energy. Printed **Moon-Watching Party** searches the
deck for Psychic Energy (one per benched Clefairy), not a look-N.

This lab uses the **app** Set F (4 Clefairy + Staraptor), not ``SET_F_NAMES`` in
``seed_data.py``. Open-stage carnival-only numbers: ``data/lab/set-ef-open-stage.md``.

E is always ``shock``. 2000 games / cell, seed `20260831`.

F 30: 4 Clefairy, Starly/Staravia/Staraptor 2/2/2, Dondozo, Orthworm, Flutter Mane,
6 Psychic / 3 Water / 3 Metal Energy, Iono, Ultra Ball, Energy Switch, Tulip,
Energy Search. Full name list: ``app_f_names`` in the JSON.

## Energy type only (still 12 Energy, ``carnival``)

Unifying to 12 Water **hurts**: Water is siphoned onto Dondozo, Power Blast falls.
The mixed 6 Psychic / 3 Water / 3 Metal is the best type-only mix here.

| Cell | F win | E win | Party games | Wonder Storm | Power Blast | Hydro Splash |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current 6P/3W/3M, carnival | **34.3%** | 65.7% | 0.0% | 15.0% | 16.3% | 5.8% |
| 12 Water, carnival | **25.9%** | 74.1% | 0.0% | 15.5% | 13.4% | 6.7% |
| 9 Water + 3 Metal, carnival | **30.6%** | 69.3% | 0.0% | 14.4% | 14.1% | 4.8% |
| 10 Water + 2 Metal, carnival | **28.5%** | 71.5% | 0.0% | 15.8% | 12.4% | 5.0% |
| 6 Psychic + 6 Water, carnival | **27.5%** | 72.5% | 0.0% | 12.7% | 13.5% | 6.7% |
| 6 Water + 6 Metal, carnival | **31.6%** | 68.5% | 0.0% | 14.3% | 14.8% | 5.9% |
| 4P/4W/4M, carnival | **33.0%** | 67.0% | 0.0% | 15.9% | 16.2% | 6.0% |

## Cut 4 Clefairy for Energy (``carnival``)

This is a Pokémon swap, not only an energy-type swap. Clefairy's Wonder Storm
wants 3 Energy for a 20×Psychic attack, so under ``carnival`` they steal fuel and
prizes. Cutting them makes the matchup close — but that cell **still does not Party**.

| Cell | F win | E win | Party games | Wonder Storm | Power Blast | Hydro Splash |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| no Clefairy +4 Water, keep other types | **49.0%** | 51.0% | 0.0% | 0.0% | 21.8% | 19.6% |
| no Clefairy, 13 Water + 3 Metal | **50.0%** | 50.0% | 0.0% | 0.0% | 22.7% | 17.0% |
| no Clefairy, 16 Water | **40.1%** | 60.0% | 0.0% | 0.0% | 18.4% | 17.1% |
| no Clefairy, 10 Psychic + 6 Water | **39.9%** | 60.1% | 0.0% | 0.0% | 20.3% | 17.4% |

## Strategy on the current 30 (keep Clefairy)

``carnival`` never uses Moon-Watching Party (0 ability uses). Named ``party`` vs
``shock`` refuses to bench Clefairy (cap 0) and looks for Mewtwo ex. Forced Party
is the line a human would try: bench Clefairy, run the printed ability, Wonder Storm.

| Cell | F win | E win | Party games | Wonder Storm | Power Blast | Hydro Splash |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current 6P/3W/3M, carnival | **34.3%** | 65.7% | 0.0% | 15.0% | 16.3% | 5.8% |
| current list, named party | **15.8%** | 84.2% | 0.0% | 45.1% | 0.0% | 1.4% |
| current list, forced Moon-Watching Party | **47.8%** | 52.2% | 62.5% | 78.4% | 0.0% | 0.1% |

## What we learned

- Two **Starly** *do* help find the bird. They are not Colorless Energy under Rule C.
- Energy **type** swaps did not beat the current 6P/3W/3M mix under ``carnival``.
- Forgetting Party was a strategy gap, not a missing attack on the card.
- Forced Party on the current list is the close matchup (~even), without cutting Clefairy.

Raw: `data/lab/set-f-party-energy.json` (elapsed 34.0s).
