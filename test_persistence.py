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
