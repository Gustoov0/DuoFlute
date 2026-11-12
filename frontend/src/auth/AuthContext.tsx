import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { api, setUnauthorizedHandler, tokenStorage } from "../lib/api";
import type { User } from "../lib/types";

interface AuthState {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState<string | null>(() => tokenStorage.get());

  // Busca os dados do usuário logado sempre que existir um token
  const me = useQuery({
    queryKey: ["me"],
    queryFn: () => api<User>("/users/me"),
    enabled: !!token,
    retry: false,
  });

  const logout = useCallback(() => {
    tokenStorage.clear();
    setToken(null);
    queryClient.clear();
  }, [queryClient]);

  // Se a API disser "não autorizado" em qualquer chamada, desloga
  useEffect(() => {
    setUnauthorizedHandler(logout);
  }, [logout]);

  const login = useCallback(async (email: string, password: string) => {
    const data = await api<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: { email, password },
      auth: false,
    });
    tokenStorage.set(data.access_token);
    setToken(data.access_token);
  }, []);

  const register = useCallback(
    async (email: string, password: string, displayName: string) => {
      await api("/auth/register", {
        method: "POST",
        body: { email, password, display_name: displayName },
        auth: false,
      });
      await login(email, password);
    },
    [login],
  );

  const value = useMemo<AuthState>(
    () => ({
      token,
      user: token ? (me.data ?? null) : null,
      loading: !!token && me.isPending,
      login,
      register,
      logout,
    }),
    [token, me.data, me.isPending, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth precisa estar dentro de <AuthProvider>");
  return ctx;
}
