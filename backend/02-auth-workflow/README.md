# Authentication workflow

bcrypt password hashing, JWT access tokens, and a React UI for register / login / protected profile.

```bash
# API — http://127.0.0.1:8000
cd backend
uv sync --dev
uv run pytest -q
uv run auth-service
```

```bash
# UI — http://127.0.0.1:5173
cd frontend
npm install
npm run dev
```

Passwords are never stored in plaintext. `/profile` requires `Authorization: Bearer <token>`. Duplicate emails return `409`. Invalid credentials return `401`.
