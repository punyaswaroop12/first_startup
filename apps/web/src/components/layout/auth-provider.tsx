"use client";

import { useRouter } from "next/navigation";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren
} from "react";

import { ApiError, authApi } from "@/lib/api";
import type { User } from "@/lib/types";

const ACCESS_TOKEN_KEY = "ops-ai-access-token";
const USER_KEY = "ops-ai-user";

interface AuthContextValue {
  token: string | null;
  user: User | null;
  isBooting: boolean;
  login: (email: string, password: string) => Promise<void>;
  completeTokenLogin: (accessToken: string, redirectTo?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isBooting, setIsBooting] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);
    const storedUser = window.localStorage.getItem(USER_KEY);

    if (!storedToken) {
      setIsBooting(false);
      return;
    }

    setToken(storedToken);
    if (storedUser) {
      setUser(JSON.parse(storedUser) as User);
    }

    authApi
      .me(storedToken)
      .then((freshUser) => {
        setUser(freshUser);
        window.localStorage.setItem(USER_KEY, JSON.stringify(freshUser));
      })
      .catch(() => {
        window.localStorage.removeItem(ACCESS_TOKEN_KEY);
        window.localStorage.removeItem(USER_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        setIsBooting(false);
      });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isBooting,
      login: async (email: string, password: string) => {
        const response = await authApi.login(email, password).catch((error: unknown) => {
          if (error instanceof ApiError) {
            throw error;
          }
          throw new Error("Unable to reach the API");
        });
        setToken(response.access_token);
        setUser(response.user);
        window.localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
        window.localStorage.setItem(USER_KEY, JSON.stringify(response.user));
        router.push("/dashboard");
      },
      completeTokenLogin: async (accessToken: string, redirectTo = "/dashboard") => {
        const freshUser = await authApi.me(accessToken).catch((error: unknown) => {
          if (error instanceof ApiError) {
            throw error;
          }
          throw new Error("Unable to reach the API");
        });
        setToken(accessToken);
        setUser(freshUser);
        window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
        window.localStorage.setItem(USER_KEY, JSON.stringify(freshUser));
        router.push(redirectTo);
      },
      logout: () => {
        window.localStorage.removeItem(ACCESS_TOKEN_KEY);
        window.localStorage.removeItem(USER_KEY);
        setToken(null);
        setUser(null);
        router.push("/login");
      }
    }),
    [isBooting, router, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
