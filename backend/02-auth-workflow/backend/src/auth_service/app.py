from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from urllib.parse import quote

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from auth_service.mailer import MailError, mail_configured, mail_provider, send_verification
from auth_service.repo import (
    DuplicateEmail,
    create_user,
    get_user_by_email,
    mark_verified,
    ping,
    rotate_verification,
)
from auth_service.schemas import LoginBody, Profile, RegisterBody, ResendBody, TokenResponse, VerifyBody
from auth_service.security import create_token, current_user, hash_password, new_verification, verify_password
from auth_service.settings import AUTH_UI_URL, CORS_ORIGIN_REGEX, CORS_ORIGINS

app = FastAPI(
    title="Auth service",
    description="Register, verify email, login, and a JWT-protected profile. Passwords are bcrypt hashes only.",
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
async def harden(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    return response


@app.get("/health")
def health() -> dict:
    return {"ok": True, "store": ping(), "mail": mail_configured(), "mail_provider": mail_provider()}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterBody) -> dict:
    email = body.email.lower()
    name = body.name.strip()
    token, expires = new_verification()
    try:
        user = create_user(
            email=email,
            name=name,
            password_hash=hash_password(body.password),
            created_at=datetime.now(timezone.utc).isoformat(),
            verification_token=token,
            verification_expires=expires,
        )
    except DuplicateEmail as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc
    mail_sent = _deliver(email, name, token)
    return {
        "id": user["id"],
        "email": email,
        "name": name,
        "email_verified": False,
        "mail_sent": mail_sent,
        "message": "Check your inbox for a verification link before signing in.",
    }


@app.post("/verify")
def verify(body: VerifyBody) -> dict:
    row = mark_verified(body.token.strip())
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link is invalid or has expired.",
        )
    return {"email": row["email"], "email_verified": True}


@app.get("/verify")
def verify_redirect(token: Annotated[str, Query(min_length=16, max_length=200)]) -> RedirectResponse:
    return RedirectResponse(url=f"{AUTH_UI_URL}/verify?token={quote(token)}", status_code=status.HTTP_302_FOUND)


@app.post("/resend-verification")
def resend(body: ResendBody) -> dict:
    email = body.email.lower()
    token, expires = new_verification()
    row = rotate_verification(email, token, expires)
    if row is not None:
        _deliver(email, row["name"], token)
    return {"ok": True, "message": "If that account exists and is unverified, a new link is on its way."}


@app.post("/login", response_model=TokenResponse)
def login(body: LoginBody) -> TokenResponse:
    row = get_user_by_email(body.email.lower())
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not row.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify your email before signing in. Check your inbox or request a new link.",
        )
    return TokenResponse(access_token=create_token(row["id"], row["email"]))


@app.get("/profile", response_model=Profile)
def profile(user: Annotated[Profile, Depends(current_user)]) -> Profile:
    return user


def _verify_url(token: str) -> str:
    return f"{AUTH_UI_URL}/verify?token={quote(token)}"


def _deliver(email: str, name: str, token: str) -> bool:
    if not mail_configured():
        return False
    try:
        send_verification(email=email, name=name, verify_url=_verify_url(token))
        return True
    except MailError:
        return False
