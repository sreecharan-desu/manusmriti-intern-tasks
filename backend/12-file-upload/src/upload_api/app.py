from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from upload_api.db import db
from upload_api.images import ALLOWED_TYPES, sniff_image_type
from upload_api.settings import MAX_BYTES, STORAGE_DIR

app = FastAPI(
    title="File upload API",
    description="JPEG/PNG uploads only. 5MB cap. Type is taken from file magic, not the client Content-Type.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with db() as connection:
        connection.execute("SELECT 1").fetchone()
    return {"ok": True}


@app.post("/uploads", status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile = File(...)) -> dict:
    data = await _read_limited(file)
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    content_type = sniff_image_type(data)
    if content_type is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG and PNG files are allowed",
        )

    suffix = ALLOWED_TYPES[content_type]
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    destination = STORAGE_DIR / stored_name
    destination.write_bytes(data)

    url = f"/files/{stored_name}"
    original_name = Path(file.filename or stored_name).name
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
        "content_type": content_type,
        "size_bytes": len(data),
        "url": url,
    }


@app.get("/uploads/{file_id}")
def get_upload(file_id: int) -> dict:
    with db() as connection:
        row = connection.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Upload not found")
    return dict(row)


@app.get("/files/{stored_name}")
def download(stored_name: str) -> FileResponse:
    safe_name = Path(stored_name).name
    if safe_name != stored_name or ".." in stored_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    path = STORAGE_DIR / safe_name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    media = "image/png" if path.suffix == ".png" else "image/jpeg"
    return FileResponse(path, media_type=media, filename=safe_name)


async def _read_limited(file: UploadFile) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="File exceeds 5MB limit",
            )
        chunks.append(chunk)
    return b"".join(chunks)
