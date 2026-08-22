import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function VerifyPage() {
  const { verify } = useAuth();
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [state, setState] = useState(token ? "pending" : "missing");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    verify(token)
      .then(() => {
        if (!cancelled) setState("ok");
      })
      .catch((err) => {
        if (!cancelled) {
          setState("error");
          setError(err.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [token, verify]);

  return (
    <main className="card">
      <p className="mono">Auth service</p>
      <h1>Email verification</h1>
      {state === "pending" ? <p className="lede">Confirming this address…</p> : null}
      {state === "ok" ? <p className="ok">This email is verified. You can sign in now.</p> : null}
      {state === "missing" ? <p className="error">This link is missing a token.</p> : null}
      {state === "error" ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      <p className="lede">
        <Link to="/login">Log in</Link>
        {" · "}
        <Link to="/register">Create another account</Link>
      </p>
    </main>
  );
}
