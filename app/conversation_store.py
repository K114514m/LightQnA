"""Persistent conversation and message storage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.app_database import get_connection, init_db


DEFAULT_CONVERSATION_TITLE = "新对话"


@dataclass(frozen=True)
class Conversation:
    """A user-owned chat conversation."""

    id: int
    user_id: int
    title: str
    created_at: str
    updated_at: str


def _row_to_conversation(row: Any) -> Conversation:
    return Conversation(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        title=str(row["title"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def _row_to_message(row: Any) -> dict[str, str]:
    return {
        "role": str(row["role"]),
        "content": str(row["content"]),
    }


def list_conversations(user_id: int) -> list[Conversation]:
    """Return all conversations for a user, newest first."""
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, user_id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = ?
            ORDER BY updated_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
    return [_row_to_conversation(row) for row in rows]


def create_conversation(user_id: int, title: str = DEFAULT_CONVERSATION_TITLE) -> Conversation:
    """Create a new conversation for a user."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO conversations (user_id, title)
            VALUES (?, ?)
            """,
            (user_id, title.strip() or DEFAULT_CONVERSATION_TITLE),
        )
        row = conn.execute(
            """
            SELECT id, user_id, title, created_at, updated_at
            FROM conversations
            WHERE id = ?
            """,
            (int(cursor.lastrowid),),
        ).fetchone()
    return _row_to_conversation(row)


def get_or_create_default_conversation(user_id: int) -> Conversation:
    """Return the newest conversation, creating one for first-time users."""
    conversations = list_conversations(user_id)
    if conversations:
        return conversations[0]
    return create_conversation(user_id)


def rename_conversation(user_id: int, conversation_id: int, title: str) -> bool:
    """Rename a user-owned conversation without changing its recency order."""
    normalized_title = title.strip() or DEFAULT_CONVERSATION_TITLE
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE conversations
            SET title = ?
            WHERE id = ? AND user_id = ?
            """,
            (normalized_title, conversation_id, user_id),
        )
    return cursor.rowcount == 1


def delete_conversation(user_id: int, conversation_id: int) -> bool:
    """Delete a user-owned conversation and its messages."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM conversations
            WHERE id = ? AND user_id = ?
            """,
            (conversation_id, user_id),
        )
    return cursor.rowcount == 1


def user_owns_conversation(user_id: int, conversation_id: int) -> bool:
    """Return whether a conversation belongs to a user."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM conversations
            WHERE id = ? AND user_id = ?
            """,
            (conversation_id, user_id),
        ).fetchone()
    return bool(row)


def add_message(
    conversation_id: int,
    role: str,
    content: str,
) -> None:
    """Append one message and touch the parent conversation."""
    if role not in {"user", "assistant"}:
        raise ValueError(f"Unsupported message role: {role}")
    if not content:
        raise ValueError("消息内容不能为空")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content),
        )
        conn.execute(
            """
            UPDATE conversations
            SET updated_at = datetime('now')
            WHERE id = ?
            """,
            (conversation_id,),
        )


def list_messages(conversation_id: int) -> list[dict[str, str]]:
    """Return all display messages for a conversation."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (conversation_id,),
        ).fetchall()
    return [_row_to_message(row) for row in rows]


def recent_history(conversation_id: int, limit: int = 10) -> list[dict[str, str]]:
    """Return recent user/assistant turns in chronological order for LightRAG."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM (
                SELECT role, content, created_at, id
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
            )
            ORDER BY created_at ASC, id ASC
            """,
            (conversation_id, limit),
        ).fetchall()
    return [
        {"role": str(row["role"]), "content": str(row["content"])}
        for row in rows
        if row["role"] in {"user", "assistant"} and row["content"]
    ]
