import { createContext, useContext, useMemo, useState } from "react";

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

  const value = useMemo(
    () => ({
      token,
      api: API,
      async register(payload) {
        const response = await fetch(`${API}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(detailMessage(body, "Registration failed"));
        return body;
      },
      async login(payload) {
        const response = await fetch(`${API}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(detailMessage(body, "Invalid email or password"));
        sessionStorage.setItem("auth_token", body.access_token);
        setToken(body.access_token);
      },
      logout() {
        sessionStorage.removeItem("auth_token");
        setToken(null);
      },
      async profile() {
        const response = await fetch(`${API}/profile`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.status === 401) {
          sessionStorage.removeItem("auth_token");
          setToken(null);
          throw new Error("Session expired");
        }
        if (!response.ok) throw new Error("Could not load profile");
        return response.json();
      },
    }),
    [token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
