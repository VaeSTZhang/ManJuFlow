import { useState } from "react";
import type { ToastMessage, ToastType } from "../components/layout/Toast";

export function useAppToasts() {
  const [toastMessages, setToastMessages] = useState<ToastMessage[]>([]);

  const dismissToast = (id: string) => {
    setToastMessages((current) => current.filter((message) => message.id !== id));
  };

  const pushToast = (type: ToastType, title: string, description?: string) => {
    const id = `${Date.now()}-${Math.random()}`;

    setToastMessages((current) => [...current, { id, type, title, description }]);
    window.setTimeout(() => dismissToast(id), 3500);
  };

  return {
    toastMessages,
    pushToast,
    dismissToast,
  };
}
