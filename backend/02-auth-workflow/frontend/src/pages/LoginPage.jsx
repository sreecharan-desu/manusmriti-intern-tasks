import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    if (!email.includes("@") || password.length < 8) {
      setError("enter a valid email and a password of at least 8 characters.");
      return;
    }
    setPending(true);
    setError("");
    try {
      await login({ email, password });
      navigate("/profile");
    } catch (err) {
      setError(err.message);
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="card">
      <p className="mono">auth service</p>
      <h1>
        <span>hi,</span>
        <span>log in</span>
      </h1>
      <p className="lede">the profile page is blocked until this returns a jwt.</p>
      <form onSubmit={onSubmit}>
        <label>
          email
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoComplete="email" required />
        </label>
        <label>
          password
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            autoComplete="current-password"
            required
          />
        </label>
        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
        <button type="submit" disabled={pending}>
          {pending ? "signing in…" : "log in"}
        </button>
      </form>
      <p className="lede">
        new here? <Link to="/register">create an account</Link>
      </p>
    </main>
  );
}
