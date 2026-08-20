from app.db import delete_chat, get_chat, init_db, list_chats, save_chat


def test_save_list_search_and_delete_chats(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    init_db()
    first = save_chat(
        [
            {"role": "user", "content": "Dondozo opening odds"},
            {"role": "assistant", "content": "About 37 percent in the first 7."},
        ]
    )
    second = save_chat(
        [
            {"role": "user", "content": "Should we trade Pikachu?"},
            {"role": "assistant", "content": "Keep Plusle as the closer."},
        ]
    )
    rows = list_chats()
    assert [row["id"] for row in rows] == [second["id"], first["id"]]
    assert rows[1]["title"].startswith("Dondozo")
    assert "37 percent" in rows[1]["preview"]
    assert rows[1]["turns"] == 1

    hits = list_chats(query="plusle")
    assert [row["id"] for row in hits] == [second["id"]]

    loaded = get_chat(first["id"])
    assert loaded["messages"][0]["content"] == "Dondozo opening odds"

    delete_chat(first["id"])
    assert get_chat(first["id"]) is None
    assert [row["id"] for row in list_chats()] == [second["id"]]
