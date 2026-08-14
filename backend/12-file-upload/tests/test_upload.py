import os
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

os.environ["UPLOAD_DB_PATH"] = str(Path("/tmp") / "manusmriti-upload-test.sqlite")
os.environ["UPLOAD_STORAGE_DIR"] = str(Path("/tmp") / "manusmriti-upload-storage")

from upload_api.app import app
from upload_api.settings import STORAGE_DIR


PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 32 + b"\xff\xd9"


def setup_function() -> None:
    Path(os.environ["UPLOAD_DB_PATH"]).unlink(missing_ok=True)
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    for path in STORAGE_DIR.glob("*"):
        if path.is_file():
            path.unlink()


def test_upload_png() -> None:
    client = TestClient(app)
    response = client.post("/uploads", files={"file": ("avatar.png", BytesIO(PNG), "image/png")})
    assert response.status_code == 201
    body = response.json()
    assert body["content_type"] == "image/png"
    stored = client.get(body["url"])
    assert stored.status_code == 200
    meta = client.get(f"/uploads/{body['id']}")
    assert meta.status_code == 200
    assert meta.json()["original_name"] == "avatar.png"


def test_upload_jpeg() -> None:
    client = TestClient(app)
    response = client.post("/uploads", files={"file": ("shot.jpg", BytesIO(JPEG), "image/jpeg")})
    assert response.status_code == 201
    assert response.json()["content_type"] == "image/jpeg"


def test_reject_pdf_even_if_labelled_png() -> None:
    client = TestClient(app)
    response = client.post("/uploads", files={"file": ("doc.png", BytesIO(b"%PDF-1.4"), "image/png")})
    assert response.status_code == 415


def test_reject_oversize() -> None:
    client = TestClient(app)
    huge = b"\x89PNG\r\n\x1a\n" + (b"x" * (5 * 1024 * 1024 + 10))
    response = client.post("/uploads", files={"file": ("big.png", BytesIO(huge), "image/png")})
    assert response.status_code == 413


def test_path_traversal_rejected() -> None:
    client = TestClient(app)
    response = client.get("/files/../secret.png")
    assert response.status_code in {400, 404}
