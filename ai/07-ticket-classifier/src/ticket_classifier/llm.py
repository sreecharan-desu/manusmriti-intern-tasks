from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

_PLACEHOLDERS = frozenset({"", "CHANGE_ME", "replace-me"})
# Verified with curl against this project's GEMINI_API_KEY (2026-08-22):
# gemini-2.0-flash / 2.5-flash → 404 retired
# gemini-3.6-flash, gemini-3.5-flash → 200 on v1beta and v1
_GEMINI_MODELS = (
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
)


class LlmError(RuntimeError):
    pass


def _secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value in _PLACEHOLDERS:
        return ""
    return value


def configured_providers() -> dict[str, bool]:
    return {
        "gemini": bool(_secret("GEMINI_API_KEY")),
        "groq": bool(_secret("GROQ_API_KEY")),
        "openai": bool(_secret("OPENAI_API_KEY")),
    }


def complete(prompt: str) -> str:
    errors: list[str] = []
    gemini_key = _secret("GEMINI_API_KEY")
    groq_key = _secret("GROQ_API_KEY")
    openai_key = _secret("OPENAI_API_KEY")

    if gemini_key:
        try:
            return _gemini(prompt, gemini_key)
        except LlmError as exc:
            errors.append(f"gemini: {exc}")
    if groq_key:
        try:
            return _openai_compatible(
                prompt,
                api_key=groq_key,
                url="https://api.groq.com/openai/v1/chat/completions",
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            )
        except LlmError as exc:
            errors.append(f"groq: {exc}")
    if openai_key:
        try:
            return _openai_compatible(
                prompt,
                api_key=openai_key,
                url="https://api.openai.com/v1/chat/completions",
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            )
        except LlmError as exc:
            errors.append(f"openai: {exc}")
    if errors:
        raise LlmError("; ".join(errors))
    raise LlmError("No GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY set")


def _openai_compatible(prompt: str, *, api_key: str, url: str, model: str) -> str:
    body = json.dumps(
        {
            "model": model,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    payload = _json_request(request)
    try:
        return payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmError("Provider returned an unexpected payload") from exc


def _gemini(prompt: str, api_key: str) -> str:
    models: list[str] = []
    preferred = os.getenv("GEMINI_MODEL", "").strip()
    if preferred in {"gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"}:
        preferred = "gemini-3.6-flash"
    for name in (preferred, *_GEMINI_MODELS):
        if name and name not in models:
            models.append(name)
    last_error: LlmError | None = None
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        request = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            method="POST",
        )
        try:
            payload = _json_request(request)
            return payload["candidates"][0]["content"]["parts"][0]["text"]
        except LlmError as exc:
            last_error = exc
            if "HTTP 404" not in str(exc) and "HTTP 400" not in str(exc):
                raise
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmError("Gemini returned an unexpected payload") from exc
    raise last_error or LlmError("Gemini request failed")


def _json_request(request: urllib.request.Request) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise LlmError(f"HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise LlmError(str(exc.reason or exc)) from exc
