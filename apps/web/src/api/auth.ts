import type { AuthLoginInput, AuthLoginOutput, InternalUser } from "../types/auth";
import { createApiErrorFromResponse } from "./errors";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function loginInternalUser(input: AuthLoginInput): Promise<AuthLoginOutput> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "登录失败，请确认账号或密码。");
  }

  return (await response.json()) as AuthLoginOutput;
}

export async function getSafeInternalUsers(): Promise<InternalUser[]> {
  const response = await fetch(`${API_BASE_URL}/api/auth/safe-users`);

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "获取内部账号列表失败。");
  }

  return (await response.json()) as InternalUser[];
}
