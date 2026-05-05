import type { ContextOptions } from "../types/scriptGeneration";

export function buildCreationContextOptions(sourceStage = "generated_script"): ContextOptions {
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
