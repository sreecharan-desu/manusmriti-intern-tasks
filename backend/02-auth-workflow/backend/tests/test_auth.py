import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ["AUTH_DB_PATH"] = str(Path("/tmp") / "manusmriti-auth-test.sqlite")
os.environ["AUTH_JWT_SECRET"] = "test-secret-must-be-at-least-32-bytes"

from auth_service.app import app
from auth_service.db import get_connection


def setup_function() -> None:
    Path(os.environ["AUTH_DB_PATH"]).unlink(missing_ok=True)


def test_register_login_and_profile() -> None:
    client = TestClient(app)
    created = client.post(
        "/register",
        json={"email": "intern@helios.example", "password": "correcthorse", "name": "Sreecharan"},
    )
    assert created.status_code == 201

    login = client.post("/login", json={"email": "intern@helios.example", "password": "correcthorse"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    profile = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["email"] == "intern@helios.example"


def test_duplicate_email() -> None:
    client = TestClient(app)
    payload = {"email": "a@b.com", "password": "correcthorse", "name": "Ada"}
    assert client.post("/register", json=payload).status_code == 201
    again = client.post("/register", json=payload)
    assert again.status_code == 409


def test_wrong_password() -> None:
    client = TestClient(app)
    client.post("/register", json={"email": "a@b.com", "password": "correcthorse", "name": "Ada"})
    login = client.post("/login", json={"email": "a@b.com", "password": "wrong-password"})
    assert login.status_code == 401


def test_profile_requires_auth() -> None:
    client = TestClient(app)
    response = client.get("/profile")
    assert response.status_code in {401, 403}


def test_garbage_token_rejected() -> None:
    client = TestClient(app)
    response = client.get("/profile", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401


def test_passwords_are_hashed() -> None:
    client = TestClient(app)
    client.post("/register", json={"email": "hash@b.com", "password": "correcthorse", "name": "Hash"})
    connection = get_connection()
    row = connection.execute("SELECT password_hash FROM users WHERE email = ?", ("hash@b.com",)).fetchone()
    connection.close()
    assert row is not None
    assert row["password_hash"] != "correcthorse"
    assert row["password_hash"].startswith("$2")


def test_short_password_rejected() -> None:
    client = TestClient(app)
    response = client.post("/register", json={"email": "x@y.com", "password": "short", "name": "Xy"})
    assert response.status_code == 422
