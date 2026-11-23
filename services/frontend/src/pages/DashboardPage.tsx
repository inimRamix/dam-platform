import { Button, Card, Typography } from "antd";
import { Navigate, useNavigate } from "react-router-dom";

import { useAuthStore } from "@/store/auth";

const { Title, Text } = Typography;

export default function DashboardPage() {
  const navigate = useNavigate();
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const displayName =
    user && user.first_name?.trim() ? user.first_name : null;

  if (!token) return <Navigate to="/login" replace />;

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Title level={3}>
            {displayName
                ? `Добро пожаловать, ${displayName}!`
                : "Добро пожаловать!"}
        </Title>
        <Text type="secondary">Роль: {user?.role ?? "…"}</Text>
        <div style={{ marginTop: 16 }}>
          <Button
            onClick={() => {
              logout();
              navigate("/login", { replace: true });
            }}
          >
            Выйти
          </Button>
        </div>
      </Card>
    </div>
  );
}
