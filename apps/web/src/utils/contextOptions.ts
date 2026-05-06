import type { AuthLoginOutput } from "../types/auth";
import type { ContextOptions } from "../types/scriptGeneration";

export function buildCreationContextOptions(
  sourceStage = "generated_script",
  authContext?: AuthLoginOutput | null,
): ContextOptions {
  if (authContext) {
    return {
      user_id: authContext.user.user_id,
      workspace_id:
        authContext.session.workspace_id ??
        authContext.user.workspace_id ??
        "workspace_dramora_internal",
      project_id: "project_creation_default",
      session_id: authContext.session.session_id,
      request_id: `request_${Date.now()}`,
      source_stage: sourceStage,
      context_policy: authContext.session.context_policy ?? "current_project_only",
    };
  }

  return {
    user_id: "internal_user_mock_001",
    workspace_id: "workspace_dramora_internal",
    project_id: "project_creation_default",
    session_id: "session_creation_default",
    request_id: `request_${Date.now()}`,
    source_stage: sourceStage,
    context_policy: "current_project_only",
  };
}
