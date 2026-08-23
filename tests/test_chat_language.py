from app.ai.chat_language import alias_card_in_text, prefers_chinese, reply_language


def test_prefers_chinese_from_hanzi():
    assert prefers_chinese("你好，皮卡丘厉害吗？")
    assert not prefers_chinese("Is Pikachu strong?")


def test_reply_language_message_wins_over_ui():
    assert reply_language("你好", "en") == "zh"
    assert reply_language("Hello", "zh") == "en"
    assert reply_language("", "zh") == "zh"


def test_alias_maps_family_cup_names():
    assert alias_card_in_text("暴噬龟在起手里吗") == "Dondozo"
    assert alias_card_in_text("皮卡丘能麻痹吗") == "Pikachu"
    assert alias_card_in_text("no hanzi here") is None
    assert alias_card_in_text("顿甲在不在") is None
    assert alias_card_in_text("故勒顿") is None
