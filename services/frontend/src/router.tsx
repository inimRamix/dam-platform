import { createBrowserRouter, Navigate } from "react-router-dom";

import AdminRoute from "@/components/AdminRoute";
import ProtectedRoute from "@/components/ProtectedRoute";
import ActivateAdminPage from "@/pages/ActivateAdminPage";
import ActivateUserPage from "@/pages/ActivateUserPage";
import DashboardPage from "@/pages/DashboardPage";
import InviteUserPage from "@/pages/InviteUserPage";
import LoginPage from "@/pages/LoginPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/admin/activate", element: <ActivateAdminPage /> },
  { path: "/users/activate", element: <ActivateUserPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      { path: "/dashboard", element: <DashboardPage /> },
      {
        element: <AdminRoute />,
        children: [{ path: "/users/invite", element: <InviteUserPage /> }],
      },
    ],
  },
  { path: "/", element: <Navigate to="/dashboard" replace /> },
  { path: "*", element: <Navigate to="/dashboard" replace /> },
]);
