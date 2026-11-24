import { Spin } from "antd";
import { Navigate, Outlet } from "react-router-dom";

import { useAuthStore } from "@/store/auth";

export default function ProtectedRoute() {
  const token = useAuthStore((s) => s.token);
  const loading = useAuthStore((s) => s.loading);

  if (loading) return <Spin fullscreen />;
  if (!token) return <Navigate to="/login" replace />;

  return <Outlet />;
}
