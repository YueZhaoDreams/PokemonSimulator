from app.engine.probability import draw_probability, hypergeometric_at_least_one


def test_dondozo_opening_hand():
    names = ["Dondozo"] + [f"Filler {i}" for i in range(27)]
    result = draw_probability("Dondozo", names, 7)
    assert result["copies"] == 1
    assert result["deck_size"] == 28
    assert abs(result["p_at_least_one"] - 7 / 28) < 1e-9


def test_zero_copies():
    names = ["Pikachu"] * 28
    result = draw_probability("Dondozo", names, 7)
    assert result["p_at_least_one"] == 0


def test_hypergeometric_full_deck():
    assert hypergeometric_at_least_one(1, 1, 1) == 1
