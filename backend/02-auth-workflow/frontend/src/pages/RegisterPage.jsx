import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    if (name.trim().length < 2 || !email.includes("@") || password.length < 8) {
      setError("Name, a valid email, and a password of at least 8 characters are required.");
      return;
    }
    setPending(true);
    setError("");
    try {
      const created = await register({ name, email, password });
      const sent = created.mail_sent ? "1" : "0";
      navigate(`/check-email?email=${encodeURIComponent(email)}&sent=${sent}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="card">
      <p className="mono">Auth service</p>
      <h1>Create account</h1>
      <form onSubmit={onSubmit}>
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" required />
        </label>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoComplete="email" required />
        </label>
        <label>
          Password
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
          />
        </label>
        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
        <button type="submit" disabled={pending}>
          {pending ? "Creating…" : "Sign up"}
        </button>
      </form>
      <p className="lede">
        Already registered? <Link to="/login">Log in</Link>
      </p>
    </main>
  );
}
