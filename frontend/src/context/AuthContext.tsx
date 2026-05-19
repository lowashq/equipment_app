import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState
} from "react";
import { useNavigate } from "react-router-dom";

import { getKeycloakLogoutUrl, getMe, login as loginRequest } from "../api/auth";
import { TokenResponse, User } from "../types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  loginWithPassword: (email: string, password: string) => Promise<void>;
  completeLogin: (response: TokenResponse) => void;
  logout: () => void;
  isRole: (...roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("token"));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(token));

  const logout = useCallback(async () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    try {
      const url = await getKeycloakLogoutUrl();
      window.location.href = url;
    } catch {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  const login = useCallback(async (newToken: string) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    const currentUser = await getMe();
    setUser(currentUser);
  }, []);

  const completeLogin = useCallback(
    (response: TokenResponse) => {
      localStorage.setItem("token", response.access_token);
      setToken(response.access_token);
      setUser(response.user);
      navigate("/dashboard", { replace: true });
    },
    [navigate]
  );

  const loginWithPassword = useCallback(
    async (email: string, password: string) => {
      const response = await loginRequest({ email, password });
      completeLogin(response);
    },
    [completeLogin]
  );

  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    getMe()
      .then((currentUser) => {
        if (isMounted) {
          setUser(currentUser);
        }
      })
      .catch(() => {
        if (isMounted) {
          localStorage.removeItem("token");
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [token]);

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      login,
      loginWithPassword,
      completeLogin,
      logout,
      isRole: (...roles: string[]) => Boolean(user && roles.includes(user.role))
    }),
    [completeLogin, isLoading, login, loginWithPassword, logout, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
