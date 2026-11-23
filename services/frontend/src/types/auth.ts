export type UserRole = "admin" | "designer" | "manager";

export interface UserMe {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: UserRole;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}
