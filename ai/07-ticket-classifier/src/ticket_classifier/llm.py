from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

_PLACEHOLDERS = frozenset({"", "CHANGE_ME", "replace-me"})


class LlmError(RuntimeError):
    pass


def _secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value in _PLACEHOLDERS:
        return ""
    return value


def complete(prompt: str) -> str:
    gemini_key = _secret("GEMINI_API_KEY")
    groq_key = _secret("GROQ_API_KEY")
    openai_key = _secret("OPENAI_API_KEY")
    if gemini_key:
        return _gemini(prompt, gemini_key)
    if groq_key:
        return _openai_compatible(
            prompt,
            openai_key=groq_key,
            url="https://api.groq.com/openai/v1/chat/completions",
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        )
    if openai_key:
        return _openai_compatible(
            prompt,
            openai_key=openai_key,
            url="https://api.openai.com/v1/chat/completions",
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )
    raise LlmError("No GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY set")


def _openai_compatible(prompt: str, *, openai_key: str, url: str, model: str) -> str:
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
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {openai_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise LlmError(str(exc)) from exc
    return payload["choices"][0]["message"]["content"]


def _gemini(prompt: str, api_key: str) -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise LlmError(str(exc)) from exc
    return payload["candidates"][0]["content"]["parts"][0]["text"]
