import importlib
import json


def _reload_modules(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    import app_database
    import auth_service
    import conversation_store

    importlib.reload(app_database)
    importlib.reload(auth_service)
    importlib.reload(conversation_store)
    return auth_service, conversation_store


def test_create_and_authenticate_user_with_hashed_password(monkeypatch, tmp_path):
    auth_service, _ = _reload_modules(monkeypatch, tmp_path)
    auth_service.init_auth_store()

    user = auth_service.create_user("alice", "secret")
    authenticated = auth_service.authenticate_user("alice", "secret")

    assert authenticated == user
    assert auth_service.authenticate_user("alice", "wrong") is None


def test_legacy_credentials_are_migrated_to_sqlite(monkeypatch, tmp_path):
    auth_service, _ = _reload_modules(monkeypatch, tmp_path)
    legacy_path = tmp_path / "user_credentials.json"
    legacy_path.write_text(
        json.dumps(
            {
                "admin": {
                    "username": "admin",
                    "password": "admin123",
                    "is_admin": True,
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(auth_service, "LEGACY_CREDENTIALS_PATH", legacy_path)

    auth_service.init_auth_store()
    user = auth_service.authenticate_user("admin", "admin123")

    assert user is not None
    assert user.is_admin is True


def test_conversation_messages_are_user_scoped_and_ordered(monkeypatch, tmp_path):
    auth_service, conversation_store = _reload_modules(monkeypatch, tmp_path)
    auth_service.init_auth_store()
    alice = auth_service.create_user("alice", "secret")
    bob = auth_service.create_user("bob", "secret")

    alice_conversation = conversation_store.create_conversation(alice.id)
    bob_conversation = conversation_store.create_conversation(bob.id)
    conversation_store.add_message(alice_conversation.id, "user", "第一问")
    conversation_store.add_message(alice_conversation.id, "assistant", "第一答")
    conversation_store.add_message(bob_conversation.id, "user", "别人问题")

    alice_messages = conversation_store.list_messages(alice_conversation.id)
    alice_history = conversation_store.recent_history(alice_conversation.id)
    bob_conversations = conversation_store.list_conversations(bob.id)

    assert [message["content"] for message in alice_messages] == ["第一问", "第一答"]
    assert alice_history == [
        {"role": "user", "content": "第一问"},
        {"role": "assistant", "content": "第一答"},
    ]
    assert [conversation.id for conversation in bob_conversations] == [bob_conversation.id]


def test_rename_conversation_is_user_scoped(monkeypatch, tmp_path):
    auth_service, conversation_store = _reload_modules(monkeypatch, tmp_path)
    auth_service.init_auth_store()
    alice = auth_service.create_user("alice", "secret")
    bob = auth_service.create_user("bob", "secret")

    alice_conversation = conversation_store.create_conversation(alice.id)

    assert conversation_store.rename_conversation(
        alice.id, alice_conversation.id, "复诊记录"
    )
    assert not conversation_store.rename_conversation(
        bob.id, alice_conversation.id, "越权改名"
    )

    [conversation] = conversation_store.list_conversations(alice.id)
    assert conversation.title == "复诊记录"


def test_delete_conversation_is_user_scoped_and_removes_messages(monkeypatch, tmp_path):
    auth_service, conversation_store = _reload_modules(monkeypatch, tmp_path)
    auth_service.init_auth_store()
    alice = auth_service.create_user("alice", "secret")
    bob = auth_service.create_user("bob", "secret")

    conversation = conversation_store.create_conversation(alice.id)
    conversation_store.add_message(conversation.id, "user", "要删除的问题")

    assert not conversation_store.delete_conversation(bob.id, conversation.id)
    assert conversation_store.list_messages(conversation.id) == [
        {"role": "user", "content": "要删除的问题"}
    ]

    assert conversation_store.delete_conversation(alice.id, conversation.id)
    assert conversation_store.list_conversations(alice.id) == []
    assert conversation_store.list_messages(conversation.id) == []


def test_legacy_message_debug_columns_are_removed(monkeypatch, tmp_path):
    auth_service, conversation_store = _reload_modules(monkeypatch, tmp_path)
    auth_service.init_auth_store()
    user = auth_service.create_user("alice", "secret")
    conversation = conversation_store.create_conversation(user.id)

    import app_database

    with app_database.get_connection() as conn:
        conn.executescript(
            """
            DROP TABLE messages;
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                ent TEXT,
                yitu TEXT,
                prompt TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content, ent, yitu, prompt)
            VALUES (?, 'assistant', '旧答', '旧实体', '旧路由', '旧配置')
            """,
            (conversation.id,),
        )

    app_database.init_db()

    with app_database.get_connection() as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(messages)")}

    assert {"ent", "yitu", "prompt"}.isdisjoint(columns)
    assert conversation_store.list_messages(conversation.id) == [
        {"role": "assistant", "content": "旧答"}
    ]
