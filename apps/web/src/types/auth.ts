export type UserRole = "admin" | "creator" | "reviewer" | "viewer";

export type UserStatus = "active" | "disabled" | "pending";

export type InternalUser = {
  user_id: string;
  username: string;
  display_name?: string | null;
  role: UserRole;
  status: UserStatus;
  workspace_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  metadata: Record<string, string | number | boolean | null>;
};

export type AuthLoginInput = {
  username: string;
  password: string;
};

export type AuthSession = {
  session_id: string;
  user_id: string;
  workspace_id?: string | null;
  role: UserRole;
  status: UserStatus;
  expires_at?: string | null;
  context_policy: string;
};

export type AuthLoginOutput = {
  user: InternalUser;
  session: AuthSession;
  access_token?: string | null;
  token_type: string;
};
