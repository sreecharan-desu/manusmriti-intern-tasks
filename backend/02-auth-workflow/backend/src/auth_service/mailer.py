from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request


def send_welcome(email: str, name: str) -> None:
    url = os.getenv("MAIL_API_URL", "").strip().rstrip("/")
    if not url:
        return
    payload = {
        "to": email,
        "subject": "Your Northwind account",
        "text": f"Hi {name},\n\nYour account is ready. Sign in with this email to open your profile.\n",
    }
    thread = threading.Thread(target=_post, args=(f"{url}/mail", payload), daemon=True)
    thread.start()


def _post(url: str, payload: dict) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(request, timeout=12).read()
    except urllib.error.URLError:
        return
