from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from upload_api.images import ALLOWED_TYPES, sniff_image_type
from upload_api.repo import get_stored_file, get_upload, ping, save_upload
from upload_api.settings import CORS_ORIGIN_REGEX, CORS_ORIGINS, MAX_BYTES

app = FastAPI(
    title="File upload API",
    description="JPEG/PNG uploads only. 5MB cap. Type is taken from file magic, not the client Content-Type.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def harden(request, call_next):
    response = await call_next(request)
    if not request.url.path.startswith("/files/"):
        response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    return response


@app.get("/health")
def health() -> dict:
    return {"ok": True, "store": ping()}


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
    original_name = Path(file.filename or stored_name).name
    meta = save_upload(
        original_name=original_name,
        stored_name=stored_name,
        content_type=content_type,
        data=data,
        url=f"/files/{stored_name}",
    )
    return {
        "id": meta["id"],
        "original_name": meta["original_name"],
        "content_type": meta["content_type"],
        "size_bytes": meta["size_bytes"],
        "url": meta["url"],
    }


@app.get("/uploads/{file_id}")
def read_upload(file_id: int) -> dict:
    row = get_upload(file_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Upload not found")
    return row


@app.get("/files/{stored_name}")
def download(stored_name: str) -> Response:
    safe_name = Path(stored_name).name
    if safe_name != stored_name or ".." in stored_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    stored = get_stored_file(safe_name)
    if stored is None:
        raise HTTPException(status_code=404, detail="File not found")
    return Response(
        content=stored["data"],
        media_type=stored["content_type"],
        headers={"Content-Disposition": f'inline; filename="{safe_name}"'},
    )


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
