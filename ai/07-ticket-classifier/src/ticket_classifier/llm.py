from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class LlmError(RuntimeError):
    pass


def complete(prompt: str) -> str:
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if gemini_key:
        return _gemini(prompt, gemini_key)
    if openai_key:
        return _openai(prompt, openai_key)
    raise LlmError("No GEMINI_API_KEY or OPENAI_API_KEY set")


def _openai(prompt: str, api_key: str) -> str:
    body = json.dumps(
        {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
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
