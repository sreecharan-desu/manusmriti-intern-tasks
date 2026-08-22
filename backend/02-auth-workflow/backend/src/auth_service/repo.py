from __future__ import annotations

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


def create_user(*, email: str, name: str, password_hash: str, created_at: str) -> dict:
    if using_mongo():
        payload = {
            "id": next_id("auth_users"),
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "created_at": created_at,
        }
        try:
            users().insert_one(payload)
        except DuplicateKeyError as exc:
            raise DuplicateEmail from exc
        payload.pop("_id", None)
        return payload
    with db() as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO users (email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (email, name, password_hash, created_at),
            )
        except IntegrityError as exc:
            raise DuplicateEmail from exc
        user_id = cursor.lastrowid
    return {"id": user_id, "email": email, "name": name, "password_hash": password_hash, "created_at": created_at}


def get_user_by_email(email: str) -> dict | None:
    if using_mongo():
        doc = users().find_one({"email": email}, {"_id": 0})
        return _user(doc) if doc else None
    with db() as connection:
        row = connection.execute(
            "SELECT id, email, name, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    if using_mongo():
        doc = users().find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        return _user(doc) if doc else None
    with db() as connection:
        row = connection.execute("SELECT id, email, name FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def _user(doc: dict) -> dict:
    payload = {
        "id": int(doc["id"]),
        "email": doc["email"],
        "name": doc["name"],
    }
    if "password_hash" in doc:
        payload["password_hash"] = doc["password_hash"]
    return payload
