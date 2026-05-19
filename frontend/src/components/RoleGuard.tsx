import { Navigate, Outlet } from "react-router-dom";

import LoadingSpinner from "./LoadingSpinner";
import { useAuth } from "../context/AuthContext";

export default function RoleGuard({ roles }: { roles: string[] }) {
  const { user, isLoading, isRole } = useAuth();

  if (isLoading) {
    return <LoadingSpinner label="Checking permissions" />;
  }

  if (!user || !isRole(...roles)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
