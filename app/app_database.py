"""SQLite persistence for users, conversations, and chat messages."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "tmp_data" / "app.db"


def database_path() -> Path:
    """Return the configured SQLite database path."""
    return Path(os.getenv("APP_DB_PATH", str(DEFAULT_DB_PATH)))


def utc_now_sql() -> str:
    """Return SQLite-compatible UTC timestamp expression."""
    return "datetime('now')"


def get_connection() -> sqlite3.Connection:
    """Open a short-lived SQLite connection with app defaults."""
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db() -> None:
    """Create app persistence tables if they do not already exist."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS auth_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
                ON conversations(user_id, updated_at DESC, id DESC);

            CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
                ON messages(conversation_id, created_at ASC, id ASC);

            CREATE INDEX IF NOT EXISTS idx_auth_sessions_token_hash
                ON auth_sessions(token_hash);

            CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at
                ON auth_sessions(expires_at);
            """
        )
        message_columns = {
            str(row["name"]) for row in conn.execute("PRAGMA table_info(messages)").fetchall()
        }
        if {"ent", "yitu", "prompt"} & message_columns:
            conn.executescript(
                """
                DROP TABLE IF EXISTS messages_new;

                CREATE TABLE messages_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );

                INSERT INTO messages_new (id, conversation_id, role, content, created_at)
                SELECT id, conversation_id, role, content, created_at
                FROM messages;

                DROP TABLE messages;
                ALTER TABLE messages_new RENAME TO messages;

                CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
                    ON messages(conversation_id, created_at ASC, id ASC);
                """
            )
