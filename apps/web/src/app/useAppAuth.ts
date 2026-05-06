import { useState } from "react";
import { loginInternalUser } from "../api/auth";
import { parseApiErrorMessage } from "../api/errors";
import type { ToastType } from "../components/layout/Toast";
import type { AuthLoginOutput } from "../types/auth";

type PushToast = (type: ToastType, title: string, description?: string) => void;

type UseAppAuthParams = {
  pushToast: PushToast;
};

export function useAppAuth({ pushToast }: UseAppAuthParams) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authContext, setAuthContext] = useState<AuthLoginOutput | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(false);

  const handleLogin = async () => {
    setIsAuthLoading(true);

    try {
      const loginOutput = await loginInternalUser({
        username: "safe_creator",
        password: "SafePass123",
      });
      setAuthContext(loginOutput);
      setIsAuthenticated(true);
      pushToast("success", "登录成功", "已进入内部试用账号。");
    } catch (error) {
      pushToast("error", "登录失败", parseApiErrorMessage(error, "登录失败，请确认账号或密码。"));
    } finally {
      setIsAuthLoading(false);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setAuthContext(null);
    pushToast("info", "已退出登录", "当前为浏览模式，登录后可操作。");
  };

  const requireLogin = () => {
    pushToast("warning", "请先登录", "请先登录后开始创作。");
  };

  return {
    isAuthenticated,
    authContext,
    isAuthLoading,
    handleLogin,
    handleLogout,
    requireLogin,
  };
}
