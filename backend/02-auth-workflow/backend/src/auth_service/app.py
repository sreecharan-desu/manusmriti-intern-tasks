from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlite3 import IntegrityError

from auth_service.db import db
from auth_service.schemas import LoginBody, Profile, RegisterBody, TokenResponse
from auth_service.security import create_token, current_user, hash_password, verify_password
from auth_service.settings import CORS_ORIGIN_REGEX, CORS_ORIGINS

app = FastAPI(
    title="Auth service",
    description="Register, login, and a JWT-protected profile. Passwords are bcrypt hashes only.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_store(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    return response


@app.get("/health")
def health() -> dict:
    with db() as connection:
        connection.execute("SELECT 1").fetchone()
    return {"ok": True}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterBody) -> dict:
    email = body.email.lower()
    name = body.name.strip()
    with db() as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO users (email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (email, name, hash_password(body.password), datetime.now(timezone.utc).isoformat()),
            )
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            ) from exc
        user_id = cursor.lastrowid
    return {"id": user_id, "email": email, "name": name}


@app.post("/login", response_model=TokenResponse)
def login(body: LoginBody) -> TokenResponse:
    with db() as connection:
        row = connection.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (body.email.lower(),),
        ).fetchone()
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=create_token(row["id"], row["email"]))


@app.get("/profile", response_model=Profile)
def profile(user: Annotated[Profile, Depends(current_user)]) -> Profile:
    return user
