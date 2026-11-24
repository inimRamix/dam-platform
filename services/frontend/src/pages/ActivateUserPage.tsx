import { App, Button, Card, Form, Input, Result, Typography } from "antd";
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth";

const { Title, Text } = Typography;

interface FormValues {
  password: string;
}

export default function ActivateUserPage() {
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
        title="Токен приглашения не найден"
        subTitle="Перейдите по ссылке из письма-приглашения."
      />
    );
  }

  const onFinish = async (values: FormValues) => {
    setLoading(true);
    try {
      const { access_token } = await authApi.activateUser(token, values);
      await setToken(access_token);
      message.success("Аккаунт активирован");
      navigate("/dashboard", { replace: true });
    } catch (err: unknown) {
      const detail =
        // @ts-expect-error axios error shape
        err?.response?.data?.detail ?? "Не удалось активировать аккаунт";
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
          Активация аккаунта
        </Title>
        <Text type="secondary">
          Задайте пароль - и вы сразу войдёте в систему.
        </Text>
        <Form<FormValues>
          layout="vertical"
          onFinish={onFinish}
          style={{ marginTop: 16 }}
        >
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
              Активировать
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
