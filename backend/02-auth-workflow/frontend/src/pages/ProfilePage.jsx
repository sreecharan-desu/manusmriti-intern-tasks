import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function ProfilePage() {
  const { profile, logout, user: cached } = useAuth();
  const navigate = useNavigate();
  const [user, setUser] = useState(cached);
  const [error, setError] = useState("");

  useEffect(() => {
    if (cached) {
      setUser(cached);
      return;
    }
    let cancelled = false;
    profile()
      .then((data) => {
        if (!cancelled) setUser(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [cached, profile]);

  function onLogout() {
    logout();
    navigate("/login");
  }

  return (
    <main className="card">
      <p className="mono">Protected</p>
      <h1>Profile</h1>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {user ? (
        <dl>
          <dt>Name</dt>
          <dd>{user.name}</dd>
          <dt>Email</dt>
          <dd>{user.email}</dd>
          <dt>Verified</dt>
          <dd>{user.email_verified ? "yes" : "no"}</dd>
        </dl>
      ) : (
        <p className="lede">Loading protected data…</p>
      )}
      <button type="button" onClick={onLogout}>
        Log out
      </button>
    </main>
  );
}
