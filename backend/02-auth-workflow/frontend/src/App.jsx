import { Navigate, Route, Routes } from "react-router-dom";
import { SiteFooter } from "./SiteFooter.jsx";
import { AuthProvider, useAuth } from "./auth.jsx";
import CheckEmailPage from "./pages/CheckEmailPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import VerifyPage from "./pages/VerifyPage.jsx";

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
          <Route path="/check-email" element={<CheckEmailPage />} />
          <Route path="/verify" element={<VerifyPage />} />
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
        <SiteFooter note="Verify email · bcrypt hashes · profile needs a JWT" />
      </div>
    </AuthProvider>
  );
}
