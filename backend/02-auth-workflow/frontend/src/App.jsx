import { Navigate, NavLink, Route, Routes } from "react-router-dom";
import { SiteFooter } from "./SiteFooter.jsx";
import { AuthProvider, useAuth } from "./auth.jsx";
import { IconKey, IconPlus, IconUser, blurDock } from "./icons.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";

function Protected({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function Shell({ children }) {
  const { token } = useAuth();
  return (
    <div className="app">
      <div className="dock-wrap">
        <nav className="site-dock" aria-label="primary">
          <NavLink to="/login" className="dock-btn" aria-label="log in" onPointerUp={blurDock}>
            <IconKey />
          </NavLink>
          <NavLink to="/register" className="dock-btn" aria-label="create account" onPointerUp={blurDock}>
            <IconPlus />
          </NavLink>
          {token ? (
            <>
              <span className="dock-divider" />
              <NavLink to="/profile" className="dock-btn" aria-label="profile" onPointerUp={blurDock}>
                <IconUser />
              </NavLink>
            </>
          ) : null}
        </nav>
      </div>
      {children}
      <SiteFooter note="passwords are bcrypt hashes · profile needs a jwt" />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Shell>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/profile"
            element={
              <Protected>
                <ProfilePage />
              </Protected>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Shell>
    </AuthProvider>
  );
}
