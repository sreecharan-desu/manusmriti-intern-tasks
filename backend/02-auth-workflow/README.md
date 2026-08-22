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

Passwords are never stored in plaintext. `/profile` requires `Authorization: Bearer <token>`. Duplicate emails return `409`. Invalid credentials return `401`. Login is `403` until the verification email is confirmed.

Verification mail is sent through the Node **nodemailer** service in `mailer/` (`MAIL_PROVIDER=nodemailer`). That is the intern-task transport. The same Python mail port can later swap to SES, Resend, or Twilio without changing register / verify.

```bash
# Mailer — http://127.0.0.1:8010
cd mailer
cp .env.example .env   # EMAIL_USER + Gmail app password
npm install
npm start
```
