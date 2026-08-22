from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from ticket_classifier.classify import classify
from ticket_classifier.lock import BusyError

app = FastAPI(
    title="Ticket classifier",
    description="Prompt → JSON → allowlist. Concurrent calls share a process/file lock.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageIn(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


@app.middleware("http")
async def no_store(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    return response


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/classify")
def classify_route(body: MessageIn) -> dict:
    try:
        return classify(body.message)
    except BusyError as exc:
        raise HTTPException(
            status_code=429,
            detail=str(exc),
            headers={"Retry-After": "2"},
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _PAGE


_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Ticket classifier</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500&family=Geist:wght@400;500;600&display=swap" rel="stylesheet" />
    <style>
      :root { --bg:#f4f0e8; --ink:#1c1914; --muted:#6b6458; --line:#e4ddd0; --paper:#fffdf8; --accent:#1f4d3a; }
      * { box-sizing: border-box; }
      body { margin:0; min-height:100vh; font-family:Geist,system-ui,sans-serif; color:var(--ink);
        background: radial-gradient(900px 420px at 8% -10%, #d7e6d8, transparent 55%), var(--bg); }
      main { width:min(36rem, calc(100% - 40px)); margin:0 auto; padding:56px 0 80px; }
      h1 { font-weight:600; letter-spacing:-.03em; font-size:clamp(1.7rem,3vw,2.2rem); margin:0 0 8px; }
      .mono { font-family:"Geist Mono",ui-monospace,monospace; font-size:12px; color:var(--muted); }
      textarea { width:100%; min-height:8rem; margin:20px 0 12px; padding:12px 14px; border:1px solid var(--line);
        border-radius:10px; font:inherit; background:var(--paper); color:var(--ink); resize:vertical; }
      textarea:focus-visible, button:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
      button { height:2.5rem; padding:0 1.25rem; border:0; border-radius:10px; background:var(--accent); color:#f6fff9;
        font:inherit; font-size:13px; font-weight:500; cursor:pointer; }
      button:disabled { opacity:.4; }
      pre { background:var(--paper); border:1px solid var(--line); border-radius:12px; padding:16px; overflow:auto;
        font-family:"Geist Mono",ui-monospace,monospace; font-size:13px; }
      .error { color:#9f1239; }
      footer { margin-top:48px; color:var(--muted); font-size:13px; }
    </style>
  </head>
  <body>
    <main>
      <p class="mono">Allowlist · no training</p>
      <h1>Classify a support message</h1>
      <p class="mono">Same-text requests share one model call. Others wait on a lock, then 429 if still busy.</p>
      <form id="form">
        <textarea name="message" maxlength="8000" required placeholder="My order hasn't arrived yet."></textarea>
        <button type="submit">Classify</button>
      </form>
      <pre id="out" hidden></pre>
      <footer>IST <span id="clock"></span></footer>
    </main>
    <script>
      const form = document.getElementById("form");
      const out = document.getElementById("out");
      const clock = document.getElementById("clock");
      let inflight = null;
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (inflight) inflight.abort();
        inflight = new AbortController();
        const button = form.querySelector("button");
        button.disabled = true;
        out.hidden = false;
        out.className = "";
        out.textContent = "…";
        try {
          const response = await fetch("/classify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: form.message.value }),
            signal: inflight.signal,
          });
          const body = await response.json();
          if (!response.ok) throw new Error(typeof body.detail === "string" ? body.detail : "Request failed");
          out.textContent = JSON.stringify(body, null, 2);
        } catch (err) {
          if (err.name === "AbortError") return;
          out.className = "error";
          out.textContent = err.message;
        } finally {
          button.disabled = false;
        }
      });
      const tick = () => {
        clock.textContent = new Date().toLocaleTimeString("en-US", {
          timeZone: "Asia/Kolkata", hour: "numeric", minute: "2-digit", second: "2-digit", hour12: true,
        }).toLowerCase();
      };
      tick();
      setInterval(tick, 1000);
    </script>
  </body>
</html>
"""
