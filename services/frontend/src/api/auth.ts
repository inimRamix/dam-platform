import { api } from "./client";
import type { LoginRequest, TokenResponse, UserMe } from "@/types/auth";

export interface AdminActivateRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface ActivateUserRequest {
  password: string;
  first_name: string;
  last_name: string;
}

export interface InviteUserRequest {
  email: string;
  role: "designer" | "manager";
}

export interface InviteResponse {
  message: string;
  email: string;
}

export const authApi = {
  login: async (data: LoginRequest) =>
    (await api.post<TokenResponse>("/v1/auth/login", data)).data,

  me: async () => (await api.get<UserMe>("/v1/auth/me")).data,

  activateAdmin: async (token: string, data: AdminActivateRequest) =>
    (
      await api.post<TokenResponse>(
        `/v1/admin/activate?token=${encodeURIComponent(token)}`,
        data,
      )
    ).data,

  activateUser: async (token: string, data: ActivateUserRequest) =>
    (
      await api.post<TokenResponse>(
        `/v1/users/activate?token=${encodeURIComponent(token)}`,
        data,
      )
    ).data,

  inviteUser: async (data: InviteUserRequest) =>
    (await api.post<InviteResponse>("/v1/users/invite", data)).data,
};
