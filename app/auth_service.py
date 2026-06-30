"""User registration and password verification."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.app_database import get_connection, init_db

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    PasswordHasher = None
    VerifyMismatchError = Exception


PBKDF2_ITERATIONS = 260_000
PBKDF2_PREFIX = "pbkdf2_sha256"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
LEGACY_CREDENTIALS_PATH = Path(__file__).resolve().parents[1] / "tmp_data" / "user_credentials.json"
SESSION_TOKEN_BYTES = 32
SESSION_TTL_DAYS = 7


@dataclass(frozen=True)
class AuthUser:
    """Authenticated user details used by Streamlit session state."""

    id: int
    username: str
    is_admin: bool


def _argon2_hasher() -> Any | None:
    if PasswordHasher is None:
        return None
    return PasswordHasher()


def _hash_pbkdf2(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return "$".join(
        [
            PBKDF2_PREFIX,
            str(PBKDF2_ITERATIONS),
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(digest).decode("ascii"),
        ]
    )


def _verify_pbkdf2(password_hash: str, password: str) -> bool:
    try:
        prefix, iterations, salt_b64, digest_b64 = password_hash.split("$", 3)
        if prefix != PBKDF2_PREFIX:
            return False
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def hash_password(password: str) -> str:
    """Hash a password with Argon2 when available, falling back to PBKDF2."""
    hasher = _argon2_hasher()
    if hasher is not None:
        return hasher.hash(password)
    return _hash_pbkdf2(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password against a stored hash."""
    if password_hash.startswith(f"{PBKDF2_PREFIX}$"):
        return _verify_pbkdf2(password_hash, password)

    hasher = _argon2_hasher()
    if hasher is None:
        return False
    try:
        return bool(hasher.verify(password_hash, password))
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def _row_to_user(row: Any) -> AuthUser:
    return AuthUser(
        id=int(row["id"]),
        username=str(row["username"]),
        is_admin=bool(row["is_admin"]),
    )


def get_user_by_username(username: str) -> AuthUser | None:
    """Return a user by username, or None when absent."""
    normalized = username.strip()
    if not normalized:
        return None
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, is_admin FROM users WHERE username = ?",
            (normalized,),
        ).fetchone()
    return _row_to_user(row) if row else None


def get_user_by_id(user_id: int) -> AuthUser | None:
    """Return a user by id, or None when absent."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, is_admin FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row_to_user(row) if row else None


def create_user(username: str, password: str, *, is_admin: bool = False) -> AuthUser:
    """Create a user with a hashed password."""
    normalized = username.strip()
    if not normalized:
        raise ValueError("用户名不能为空")
    if not password:
        raise ValueError("密码不能为空")

    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (?, ?, ?)
                """,
                (normalized, hash_password(password), int(is_admin)),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("用户名已存在") from exc
        user_id = int(cursor.lastrowid)
    return AuthUser(id=user_id, username=normalized, is_admin=is_admin)


def authenticate_user(username: str, password: str) -> AuthUser | None:
    """Authenticate a username/password pair."""
    normalized = username.strip()
    if not normalized or not password:
        return None
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, username, password_hash, is_admin
            FROM users
            WHERE username = ?
            """,
            (normalized,),
        ).fetchone()
    if not row or not verify_password(str(row["password_hash"]), password):
        return None
    return _row_to_user(row)


def _session_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def cleanup_expired_auth_sessions() -> None:
    """Remove expired persistent login sessions."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM auth_sessions WHERE expires_at <= datetime('now')"
        )


def create_auth_session(user_id: int, ttl_days: int = SESSION_TTL_DAYS) -> str:
    """Create a persistent login session and return its raw token."""
    if get_user_by_id(user_id) is None:
        raise ValueError("用户不存在")

    cleanup_expired_auth_sessions()
    token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO auth_sessions (user_id, token_hash, expires_at)
            VALUES (?, ?, datetime('now', ?))
            """,
            (user_id, _session_token_hash(token), f"+{ttl_days} days"),
        )
    return token


def get_user_by_session_token(token: str | None) -> AuthUser | None:
    """Return the user for a valid persistent login token."""
    if not token:
        return None

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT users.id, users.username, users.is_admin
            FROM auth_sessions
            JOIN users ON users.id = auth_sessions.user_id
            WHERE auth_sessions.token_hash = ?
              AND auth_sessions.expires_at > datetime('now')
            """,
            (_session_token_hash(token),),
        ).fetchone()
    return _row_to_user(row) if row else None


def revoke_auth_session(token: str | None) -> None:
    """Revoke one persistent login token."""
    if not token:
        return
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM auth_sessions WHERE token_hash = ?",
            (_session_token_hash(token),),
        )


def _legacy_credentials() -> dict[str, dict[str, Any]]:
    if not LEGACY_CREDENTIALS_PATH.exists():
        return {}
    try:
        data = json.loads(LEGACY_CREDENTIALS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        str(username): value
        for username, value in data.items()
        if isinstance(value, dict)
    }


def _user_count() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    return int(row["count"])


def migrate_legacy_credentials_if_empty() -> int:
    """Import legacy plaintext JSON users only when the users table is empty."""
    if _user_count() > 0:
        return 0

    legacy_users = _legacy_credentials()
    if not legacy_users:
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
        create_user(DEFAULT_ADMIN_USERNAME, default_password, is_admin=True)
        return 1

    created = 0
    for username, payload in legacy_users.items():
        password = str(payload.get("password", ""))
        if not password:
            continue
        create_user(
            username,
            password,
            is_admin=bool(payload.get("is_admin", False)),
        )
        created += 1
    return created


def init_auth_store() -> None:
    """Initialize auth persistence and bootstrap users."""
    init_db()
    migrate_legacy_credentials_if_empty()
