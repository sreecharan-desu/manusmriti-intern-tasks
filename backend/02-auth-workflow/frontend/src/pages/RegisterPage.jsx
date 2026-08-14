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
      setError("name, a valid email, and a password of at least 8 characters are required.");
      return;
    }
    setPending(true);
    setError("");
    try {
      await register({ name, email, password });
      navigate("/login");
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
        <span>create account</span>
      </h1>
      <form onSubmit={onSubmit}>
        <label>
          name
          <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" required />
        </label>
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
          {pending ? "creating…" : "sign up"}
        </button>
      </form>
      <p className="lede">
        already registered? <Link to="/login">log in</Link>
      </p>
    </main>
  );
}
