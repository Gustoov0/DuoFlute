import { Navigate, Outlet } from "react-router";

import Spinner from "../components/Spinner";
import { useAuth } from "./AuthContext";

/** Protege rotas: sem login, redireciona para /login. */
export default function RequireAuth() {
  const { token, user, loading } = useAuth();

  if (!token) return <Navigate to="/login" replace />;
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}
