from __future__ import annotations

import json
import os
import smtplib
import urllib.error
import urllib.request
from email.message import EmailMessage

_PLACEHOLDERS = frozenset({"", "CHANGE_ME", "replace-me", "placeholder"})


class MailError(RuntimeError):
    pass


def _secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    return "" if value in _PLACEHOLDERS else value


def _mail_api_url() -> str:
    value = _secret("MAIL_API_URL").rstrip("/")
    if not value.startswith(("http://", "https://")):
        return ""
    return value


def mail_configured() -> bool:
    if _mail_api_url():
        return True
    user = _secret("EMAIL_USER")
    return bool(user and "@" in user and _secret("EMAIL_PASS"))


def mail_provider() -> str:
    if _mail_api_url():
        return "nodemailer"
    if mail_configured():
        return "smtp"
    return "none"


def send_verification(*, email: str, name: str, verify_url: str) -> None:
    subject = "Verify your email"
    text = (
        f"Hi {name},\n\n"
        "Confirm this address belongs to you. Until you do, this account cannot sign in.\n\n"
        f"{verify_url}\n\n"
        "This link expires in 24 hours. If you did not create an account, ignore this email.\n"
    )
    html = (
        f"<p>Hi {name},</p>"
        "<p>Confirm this address belongs to you. Until you do, this account cannot sign in.</p>"
        f'<p><a href="{verify_url}">Verify email</a></p>'
        "<p>This link expires in 24 hours. If you did not create an account, ignore this email.</p>"
    )
    send_mail(to=email, subject=subject, text=text, html=html)


def send_mail(*, to: str, subject: str, text: str, html: str = "") -> None:
    # MAIL_PROVIDER=nodemailer today. Swap to ses / resend / twilio later without
    # changing register / verify — only this port.
    provider = os.getenv("MAIL_PROVIDER", "nodemailer").strip().lower() or "nodemailer"
    if provider == "nodemailer" and _mail_api_url():
        _via_nodemailer(to=to, subject=subject, text=text, html=html)
        return
    if provider in {"smtp", "ses", "nodemailer"} and _secret("EMAIL_USER") and _secret("EMAIL_PASS"):
        _via_smtp(to=to, subject=subject, text=text, html=html)
        return
    if provider in {"resend", "twilio"}:
        raise MailError(f"{provider} is not wired yet — keep MAIL_PROVIDER=nodemailer for this task")
    raise MailError("Mail is not configured")


def _via_nodemailer(*, to: str, subject: str, text: str, html: str) -> None:
    url = _mail_api_url()
    if not url.endswith("/mail"):
        url = f"{url}/mail"
    payload = {"to": to, "subject": subject, "text": text}
    if html:
        payload["html"] = html
    headers = {"Content-Type": "application/json"}
    secret = _secret("MAIL_API_SECRET")
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            body = json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        raise MailError(f"nodemailer HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise MailError(str(exc.reason or exc)) from exc
    if body.get("ok") is False:
        raise MailError(body.get("error") or "nodemailer rejected the message")


def _via_smtp(*, to: str, subject: str, text: str, html: str) -> None:
    user = _secret("EMAIL_USER")
    password = _secret("EMAIL_PASS")
    origin = _secret("EMAIL_FROM") or user
    host = _secret("SMTP_HOST") or "smtp.gmail.com"
    port = int(os.getenv("SMTP_PORT", "465"))
    message = EmailMessage()
    message["From"] = origin
    message["To"] = to
    message["Subject"] = subject
    message.set_content(text)
    if html:
        message.add_alternative(html, subtype="html")
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=12) as smtp:
                smtp.login(user, password)
                smtp.send_message(message)
            return
        with smtplib.SMTP(host, port, timeout=12) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(message)
    except smtplib.SMTPException as exc:
        raise MailError("SMTP send failed") from exc
