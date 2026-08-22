import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function CheckEmailPage() {
  const { resend } = useAuth();
  const [params] = useSearchParams();
  const [email, setEmail] = useState(params.get("email") || "");
  const sent = params.get("sent");
  const [note, setNote] = useState(
    sent === "0"
      ? "The account is waiting on verification, but the mailer could not deliver a message yet."
      : "",
  );
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function onResend(event) {
    event.preventDefault();
    if (!email.includes("@")) {
      setError("Enter the email you registered with.");
      return;
    }
    setPending(true);
    setError("");
    setNote("");
    try {
      await resend(email);
      setNote("If that account is still unverified, a new link is on its way.");
    } catch (err) {
      setError(err.message);
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="card">
      <p className="mono">Auth service</p>
      <h1>Check your inbox</h1>
      <p className="lede">
        Sign-in stays blocked until this address is confirmed, so a fake mailbox cannot open a
        profile.
      </p>
      <form onSubmit={onResend}>
        <label>
          Email
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            autoComplete="email"
            required
          />
        </label>
        {note ? <p className="ok">{note}</p> : null}
        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
        <button type="submit" disabled={pending}>
          {pending ? "Sending…" : "Resend verification email"}
        </button>
      </form>
      <p className="lede">
        Already verified? <Link to="/login">Log in</Link>
      </p>
    </main>
  );
}
