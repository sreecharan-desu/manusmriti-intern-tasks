import { Navigate, Route, Routes } from "react-router-dom";
import { SiteFooter } from "./SiteFooter.jsx";
import { AuthProvider, useAuth } from "./auth.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";

function Protected({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <div className="app">
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
        <SiteFooter note="Passwords are bcrypt hashes · profile needs a JWT" />
      </div>
    </AuthProvider>
  );
}
