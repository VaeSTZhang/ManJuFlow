import type { AuthLoginOutput } from "../types/auth";
import type { ContextOptions } from "../types/scriptGeneration";

export type ProjectSessionContext = {
  projectId: string;
  sessionId: string;
};

export type BuildContextOptions = (
  sourceStage?: string,
  requestIdPrefix?: string,
) => ContextOptions;

export function buildCreationContextOptions(
  sourceStage = "generated_script",
  authContext?: AuthLoginOutput | null,
  projectSessionContext?: ProjectSessionContext | null,
  requestIdPrefix = "request",
): ContextOptions {
  const projectId = projectSessionContext?.projectId ?? "project_creation_default";
  const sessionId =
    projectSessionContext?.sessionId ??
    authContext?.session.session_id ??
    "session_creation_default";

  if (authContext) {
    return {
      user_id: authContext.user.user_id,
      workspace_id:
        authContext.session.workspace_id ??
        authContext.user.workspace_id ??
        "workspace_dramora_internal",
      project_id: projectId,
      session_id: sessionId,
      request_id: `${requestIdPrefix}_${Date.now()}`,
      source_stage: sourceStage,
      context_policy: authContext.session.context_policy ?? "current_project_only",
    };
  }

  return {
    user_id: "internal_user_mock_001",
    workspace_id: "workspace_dramora_internal",
    project_id: projectId,
    session_id: sessionId,
    request_id: `${requestIdPrefix}_${Date.now()}`,
    source_stage: sourceStage,
    context_policy: "current_project_only",
  };
}
