# Manusmriti intern tasks

Sreecharan Desu · B.Tech CS, IIIT Andhra Pradesh · 2027

Three independently runnable apps for the **AI Developer Intern** round: a bcrypt/JWT auth service with a React UI, a magic-byte file upload API, and a prompt-based ticket classifier. Product engineering only. No training. No notebooks.

## Layout

```
backend/02-auth-workflow          bcrypt + JWT API and React login
backend/12-file-upload            JPEG/PNG uploads, 5MB, magic-byte check
ai/07-ticket-classifier           Gemini/OpenAI JSON → category allowlist
```

Python apps are [uv](https://docs.astral.sh/uv/) packages (`src/` layout, lockfile, `pytest`). The auth UI is Vite + React 19.

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

Copy `.env.example` for local keys. Do not commit real secrets. Classifier works without a key (offline fallback). Auth uses `AUTH_JWT_SECRET`.

## What each task proves

**Auth.** Passwords stored only as bcrypt hashes. Login returns a JWT. `/profile` requires `Authorization: Bearer`. Duplicate email is `409`. The UI keeps the token in `sessionStorage` and fetches `/profile` once per session.

**File upload.** Multipart `POST /uploads`. Size cap is `413`. Type is sniffed from magic bytes, so a PDF renamed to `.png` is `415`. Stored names are UUIDs; download paths are sanitized.

**Ticket classifier.** Prompt → Gemini or OpenAI → JSON → allowlist. Illegal categories are rejected. Empty input never hits the model. Concurrent same-text requests share one in-flight call. Other calls wait on a thread + file lock and get `429` if the wait budget is exceeded. One retry, then a keyword fallback.

## Production

Each app is its own Vercel project. APIs set `Cache-Control: no-store`. SQLite and upload storage on Vercel live under `/tmp` unless `MONGO_URI` is set (then auth users and upload bytes persist). Env values on Vercel are set through the CLI or dashboard — this repo only ships placeholders.

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
