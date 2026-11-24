import { create } from "zustand";

import { authApi } from "@/api/auth";
import { TOKEN_KEY } from "@/constants";
import type { LoginRequest, UserMe } from "@/types/auth";

interface AuthState {
  token: string | null;
  user: UserMe | null;
  loading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  loadMe: () => Promise<void>;
  setToken: (token: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem(TOKEN_KEY),
  user: null,
  loading: !!localStorage.getItem(TOKEN_KEY),

  login: async (data) => {
    const { access_token } = await authApi.login(data);
    localStorage.setItem(TOKEN_KEY, access_token);
    set({ token: access_token });
    await useAuthStore.getState().loadMe();
  },

  loadMe: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return;
    set({ loading: true });
    try {
      const user = await authApi.me();
      set({ user });
    } catch {
      localStorage.removeItem(TOKEN_KEY);
      set({ token: null, user: null });
    } finally {
      set({ loading: false });
    }
  },

  setToken: async (token) => {
    localStorage.setItem(TOKEN_KEY, token);
    set({ token });
    await useAuthStore.getState().loadMe();
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    set({ token: null, user: null });
  },
}));
