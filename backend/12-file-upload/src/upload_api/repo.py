from __future__ import annotations

from bson.binary import Binary

from upload_api.db import db
from upload_api.mongo import files, next_id, using_mongo
from upload_api.settings import STORAGE_DIR


def ping() -> str:
    if using_mongo():
        files().database.client.admin.command("ping")
        return "mongo"
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with db() as connection:
        connection.execute("SELECT 1").fetchone()
    return "sqlite"


def save_upload(
    *,
    original_name: str,
    stored_name: str,
    content_type: str,
    data: bytes,
    url: str,
) -> dict:
    if using_mongo():
        payload = {
            "id": next_id("upload_files"),
            "original_name": original_name,
            "stored_name": stored_name,
            "content_type": content_type,
            "size_bytes": len(data),
            "url": url,
            "bytes": Binary(data),
        }
        files().insert_one(payload)
        return _meta(payload)
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    (STORAGE_DIR / stored_name).write_bytes(data)
    with db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO files (original_name, stored_name, content_type, size_bytes, url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (original_name, stored_name, content_type, len(data), url),
        )
        file_id = cursor.lastrowid
    return {
        "id": file_id,
        "original_name": original_name,
        "stored_name": stored_name,
        "content_type": content_type,
        "size_bytes": len(data),
        "url": url,
    }


def get_upload(file_id: int) -> dict | None:
    if using_mongo():
        doc = files().find_one({"id": file_id}, {"_id": 0, "bytes": 0})
        return _meta(doc) if doc else None
    with db() as connection:
        row = connection.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    return dict(row) if row else None


def get_stored_file(stored_name: str) -> dict | None:
    if using_mongo():
        doc = files().find_one({"stored_name": stored_name}, {"_id": 0})
        if doc is None:
            return None
        return {"content_type": doc["content_type"], "data": bytes(doc["bytes"])}
    path = STORAGE_DIR / stored_name
    if not path.is_file():
        return None
    media = "image/png" if path.suffix == ".png" else "image/jpeg"
    return {"content_type": media, "data": path.read_bytes()}


def _meta(doc: dict) -> dict:
    return {
        "id": int(doc["id"]),
        "original_name": doc["original_name"],
        "stored_name": doc["stored_name"],
        "content_type": doc["content_type"],
        "size_bytes": int(doc["size_bytes"]),
        "url": doc["url"],
    }
