# Manusmriti intern tasks

Sreecharan Desu · B.Tech CS, IIIT Andhra Pradesh · 2027

Three independently runnable projects for the **AI Developer Intern** round at MANUSMRITI: auth (API + UI), file uploads, and a structured LLM classifier. Each one has tests, a README, and a single command to start.

This is product engineering: HTTP APIs, auth, uploads, and a model call with a hard allowlist. No training. No notebooks.

## Layout

```
backend/02-auth-workflow          bcrypt + JWT API and React login
backend/12-file-upload            JPEG/PNG uploads, 5MB, magic-byte check
ai/07-ticket-classifier           Gemini/Groq/OpenAI JSON → category allowlist
```

Python apps are [uv](https://docs.astral.sh/uv/) packages (`src/` layout, lockfile, `pytest`). The auth UI is Vite + React.

## Run

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), and Node 22+.

```bash
# Auth API + UI        http://127.0.0.1:8000  ·  http://127.0.0.1:5173
cd backend/02-auth-workflow/backend && uv sync --dev && uv run pytest -q && uv run auth-service
cd backend/02-auth-workflow/frontend && npm install && npm run dev

# File upload API      http://127.0.0.1:8002/docs
cd backend/12-file-upload && uv sync --dev && uv run pytest -q && uv run upload-api

# Ticket classifier
cd ai/07-ticket-classifier && uv sync --dev && uv run pytest -q
uv run classify "My order hasn't arrived yet."
```

Copy `.env.example` where you want keys. Classifier works without an API key (offline fallback). Auth uses `AUTH_JWT_SECRET`.

Do not commit real keys. Vercel env vars are placeholders until you paste production values in the dashboard.

Upload storage on Vercel lives under `/tmp` (ephemeral between cold starts). The same apps use a local disk file when you run them with uv.

## What each task proves

**Auth.** Passwords stored only as bcrypt hashes. Login returns a JWT. `/profile` requires `Authorization: Bearer`. Duplicate email is `409`. React UI for register, login, protected profile, logout.

**File upload.** Multipart `POST /uploads`. Size cap is `413`. Type is sniffed from magic bytes, not the client `Content-Type`, so a PDF renamed to `.png` is `415`. Stored names are UUIDs; download paths are sanitized.

**Ticket classifier.** Prompt → Gemini, Groq, or OpenAI → JSON → allowlist. Illegal categories are rejected in `parse.py`. Empty input never hits the model. One retry, then a keyword fallback so the CLI demos without keys.

## Production

Each app is its own Vercel project. APIs set `Cache-Control: no-store`. The classifier serializes overlapping model calls with a thread lock plus a file lock and returns `429` if the wait budget is exceeded. The auth UI caches `/profile` for the session so React Strict Mode does not double-fetch.

| App | Production URL |
| --- | --- |
| Auth API | https://manusmriti-auth-api.vercel.app |
| Auth UI | https://manusmriti-auth-ui.vercel.app |
| Upload API | https://manusmriti-upload-api.vercel.app |
| Ticket classifier | https://manusmriti-ticket-classifier.vercel.app |

## Ports

| App | Port |
| --- | ---: |
| Auth API | 8000 |
| Upload API | 8002 |
| Auth UI | 5173 |
