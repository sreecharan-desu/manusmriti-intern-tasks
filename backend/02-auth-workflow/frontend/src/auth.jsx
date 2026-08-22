import { createContext, useContext, useMemo, useRef, useState } from "react";

const AuthContext = createContext(null);
const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function detailMessage(body, fallback) {
  if (typeof body?.detail === "string") return body.detail;
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item) => item.msg || JSON.stringify(item)).join(" ");
  }
  return fallback;
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => sessionStorage.getItem("auth_token"));
  const [user, setUser] = useState(null);
  const inflight = useRef(null);

  const value = useMemo(
    () => ({
      token,
      user,
      api: API,
      async register(payload) {
        const response = await fetch(`${API}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "omit",
          body: JSON.stringify(payload),
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(detailMessage(body, "Registration failed"));
        return body;
      },
      async verify(token) {
        const response = await fetch(`${API}/verify`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "omit",
          body: JSON.stringify({ token }),
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(detailMessage(body, "Verification failed"));
        return body;
      },
      async resend(email) {
        const response = await fetch(`${API}/resend-verification`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "omit",
          body: JSON.stringify({ email }),
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(detailMessage(body, "Could not resend"));
        return body;
      },
      async login(payload) {
        const response = await fetch(`${API}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "omit",
          body: JSON.stringify(payload),
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(detailMessage(body, "Invalid email or password"));
        sessionStorage.setItem("auth_token", body.access_token);
        setUser(null);
        inflight.current = null;
        setToken(body.access_token);
      },
      logout() {
        sessionStorage.removeItem("auth_token");
        inflight.current = null;
        setUser(null);
        setToken(null);
      },
      async profile() {
        if (user) return user;
        if (inflight.current) return inflight.current;
        const request = fetch(`${API}/profile`, {
          headers: { Authorization: `Bearer ${token}` },
          credentials: "omit",
        }).then(async (response) => {
          if (response.status === 401) {
            sessionStorage.removeItem("auth_token");
            setToken(null);
            setUser(null);
            throw new Error("Session expired");
          }
          if (!response.ok) throw new Error("Could not load profile");
          const data = await response.json();
          setUser(data);
          return data;
        });
        inflight.current = request;
        try {
          return await request;
        } finally {
          inflight.current = null;
        }
      },
    }),
    [token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
