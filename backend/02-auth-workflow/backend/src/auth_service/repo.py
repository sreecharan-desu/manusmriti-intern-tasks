from __future__ import annotations

from datetime import datetime, timezone
from sqlite3 import IntegrityError

from pymongo.errors import DuplicateKeyError

from auth_service.db import db
from auth_service.mongo import next_id, users, using_mongo


class DuplicateEmail(Exception):
    pass


def ping() -> str:
    if using_mongo():
        users().database.client.admin.command("ping")
        return "mongo"
    with db() as connection:
        connection.execute("SELECT 1").fetchone()
    return "sqlite"


def create_user(
    *,
    email: str,
    name: str,
    password_hash: str,
    created_at: str,
    verification_token: str,
    verification_expires: str,
) -> dict:
    payload = {
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "created_at": created_at,
        "email_verified": False,
        "verification_token": verification_token,
        "verification_expires": verification_expires,
    }
    if using_mongo():
        payload["id"] = next_id("auth_users")
        try:
            users().insert_one(payload)
        except DuplicateKeyError as exc:
            raise DuplicateEmail from exc
        payload.pop("_id", None)
        return payload
    with db() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO users (
                    email, name, password_hash, created_at,
                    email_verified, verification_token, verification_expires
                ) VALUES (?, ?, ?, ?, 0, ?, ?)
                """,
                (email, name, password_hash, created_at, verification_token, verification_expires),
            )
        except IntegrityError as exc:
            raise DuplicateEmail from exc
        payload["id"] = cursor.lastrowid
    return payload


def get_user_by_email(email: str) -> dict | None:
    if using_mongo():
        doc = users().find_one({"email": email}, {"_id": 0})
        return _user(doc) if doc else None
    with db() as connection:
        row = connection.execute(
            """
            SELECT id, email, name, password_hash, email_verified,
                   verification_token, verification_expires
            FROM users WHERE email = ?
            """,
            (email,),
        ).fetchone()
    return _row(row)


def get_user_by_id(user_id: int) -> dict | None:
    if using_mongo():
        doc = users().find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        return _user(doc) if doc else None
    with db() as connection:
        row = connection.execute(
            "SELECT id, email, name, email_verified FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row(row)


def mark_verified(token: str) -> dict | None:
    now = datetime.now(timezone.utc).isoformat()
    if using_mongo():
        doc = users().find_one({"verification_token": token}, {"_id": 0})
        if not doc:
            return None
        expires = str(doc.get("verification_expires") or "")
        if expires and expires < now and not doc.get("email_verified"):
            return None
        if not doc.get("email_verified"):
            users().update_one({"verification_token": token}, {"$set": {"email_verified": True}})
            doc["email_verified"] = True
        return _user(doc)
    with db() as connection:
        row = connection.execute(
            """
            SELECT id, email, name, email_verified, verification_expires
            FROM users WHERE verification_token = ?
            """,
            (token,),
        ).fetchone()
        if row is None:
            return None
        expires = row["verification_expires"] or ""
        if expires and expires < now and not row["email_verified"]:
            return None
        if not row["email_verified"]:
            connection.execute(
                "UPDATE users SET email_verified = 1 WHERE verification_token = ?",
                (token,),
            )
    return {"id": row["id"], "email": row["email"], "name": row["name"], "email_verified": True}


def rotate_verification(email: str, token: str, expires: str) -> dict | None:
    row = get_user_by_email(email)
    if row is None or row.get("email_verified"):
        return None
    if using_mongo():
        users().update_one(
            {"email": email},
            {"$set": {"verification_token": token, "verification_expires": expires}},
        )
        row["verification_token"] = token
        row["verification_expires"] = expires
        return row
    with db() as connection:
        connection.execute(
            "UPDATE users SET verification_token = ?, verification_expires = ? WHERE email = ?",
            (token, expires, email),
        )
    row["verification_token"] = token
    row["verification_expires"] = expires
    return row


def _row(row) -> dict | None:
    return _user(dict(row)) if row is not None else None


def _user(doc: dict) -> dict:
    payload = {
        "id": int(doc["id"]),
        "email": doc["email"],
        "name": doc["name"],
        "email_verified": _verified(doc),
    }
    if "password_hash" in doc:
        payload["password_hash"] = doc["password_hash"]
    if "verification_token" in doc:
        payload["verification_token"] = doc.get("verification_token")
    if "verification_expires" in doc:
        payload["verification_expires"] = doc.get("verification_expires")
    return payload


def _verified(doc: dict) -> bool:
    if "email_verified" not in doc:
        return True
    return bool(doc["email_verified"])
