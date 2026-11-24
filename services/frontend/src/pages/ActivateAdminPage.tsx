import { App, Button, Card, Form, Input, Result, Typography } from "antd";
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth";

const { Title } = Typography;

interface FormValues {
  email: string;
  password: string;
}

export default function ActivateAdminPage() {
  const { message } = App.useApp();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const setToken = useAuthStore((s) => s.setToken);
  const [loading, setLoading] = useState(false);

  const token = params.get("token");

  if (!token) {
    return (
      <Result
        status="error"
        title="Токен активации не найден"
        subTitle="Перейдите по ссылке из письма или запросите новую у администратора сервера."
      />
    );
  }

  const onFinish = async (values: FormValues) => {
    setLoading(true);
    try {
      const { access_token } = await authApi.activateAdmin(token, values);
      await setToken(access_token);
      message.success("Администратор создан");
      navigate("/dashboard", { replace: true });
    } catch (err: unknown) {
      const detail =
        // @ts-expect-error axios error shape
        err?.response?.data?.detail ?? "Не удалось активировать администратора";
      message.error(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        background: "#f0f2f5",
      }}
    >
      <Card style={{ width: 420 }}>
        <Title level={2} style={{ textAlign: "center" }}>
          Создание администратора
        </Title>
        <Form<FormValues> layout="vertical" onFinish={onFinish}>
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: "Введите email" },
              { type: "email", message: "Некорректный email" },
            ]}
          >
            <Input placeholder="admin@company.com" autoComplete="email" />
          </Form.Item>
          <Form.Item
            label="Пароль"
            name="password"
            rules={[
              { required: true, message: "Введите пароль" },
              { min: 8, message: "Минимум 8 символов" },
            ]}
          >
            <Input.Password autoComplete="new-password" />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              Создать администратора
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
