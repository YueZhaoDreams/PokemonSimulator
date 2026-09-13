from app.engine.probability import draw_probability, hypergeometric_at_least_one


def test_dondozo_opening_hand():
    names = ["Dondozo"] + [f"Filler {i}" for i in range(29)]
    result = draw_probability("Dondozo", names, 7)
    assert result["copies"] == 1
    assert result["deck_size"] == 30
    assert abs(result["p_at_least_one"] - 7 / 30) < 1e-9


def test_zero_copies():
    names = ["Pikachu"] * 28
    result = draw_probability("Dondozo", names, 7)
    assert result["p_at_least_one"] == 0


def test_more_copies_than_draw_does_not_crash():
    # 17 Psychic Energy in a 60: exact counts above the draw size are impossible, not an error.
    names = ["Psychic Energy"] * 17 + [f"Filler {i}" for i in range(43)]
    result = draw_probability("Psychic Energy", names, 7)
    assert result["copies"] == 17
    assert result["exact"]["8"] == 0.0
    assert abs(sum(result["exact"].values()) - 1.0) < 1e-9
    assert abs(result["p_at_least_one"] - (1 - result["exact"]["0"])) < 1e-9


def test_hypergeometric_full_deck():
    assert hypergeometric_at_least_one(1, 1, 1) == 1
