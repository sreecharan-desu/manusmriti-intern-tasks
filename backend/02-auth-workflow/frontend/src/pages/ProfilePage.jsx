import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function ProfilePage() {
  const { profile, logout } = useAuth();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
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
  }, [profile]);

  function onLogout() {
    logout();
    navigate("/login");
  }

  return (
    <main className="card">
      <p className="eyebrow">Protected</p>
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
          <dt>User ID</dt>
          <dd>{user.id}</dd>
        </dl>
      ) : (
        <p className="muted">Loading protected data…</p>
      )}
      <button type="button" onClick={onLogout}>
        Log out
      </button>
    </main>
  );
}
