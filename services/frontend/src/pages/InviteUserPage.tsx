import { App, Button, Card, Form, Input, Select, Typography } from "antd";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { authApi, type InviteUserRequest } from "@/api/auth";

const { Title, Text } = Typography;

export default function InviteUserPage() {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [form] = Form.useForm<InviteUserRequest>();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: InviteUserRequest) => {
    setLoading(true);
    try {
      const res = await authApi.inviteUser(values);
      message.success(res.message);
      form.resetFields();
      navigate("/dashboard");
    } catch (err: unknown) {
      const detail =
        // @ts-expect-error axios error shape
        err?.response?.data?.detail ?? "Не удалось отправить приглашение";
      message.error(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 520, margin: "0 auto" }}>
      <Card>
        <Title level={3}>Приглашение пользователя</Title>
        <Text type="secondary">
          На указанный email придёт письмо со ссылкой для активации.
        </Text>
        <Form<InviteUserRequest>
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{ role: "designer" }}
          style={{ marginTop: 16 }}
        >
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: "Введите email" },
              { type: "email", message: "Некорректный email" },
            ]}
          >
            <Input placeholder="user@company.com" />
          </Form.Item>
          <Form.Item label="Роль" name="role">
            <Select
              options={[
                { value: "designer", label: "Дизайнер" },
                { value: "manager", label: "Менеджер" },
              ]}
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              Отправить приглашение
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
