import { useCallback, useEffect, useState } from "react";
import type { AuthLoginOutput } from "../types/auth";
import type { BuildContextOptions } from "../utils/contextOptions";
import { buildCreationContextOptions } from "../utils/contextOptions";

const DEFAULT_PROJECT_ID = "project_creation_default";
const DEFAULT_SESSION_ID = "session_creation_default";

type UseProjectSessionContextParams = {
  authContext?: AuthLoginOutput | null;
};

function sanitizeContextIdPart(value: string | null | undefined): string {
  const sanitized = (value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, "_")
    .replace(/^_+|_+$/g, "");

  return sanitized || "internal";
}

function buildProjectId(authContext?: AuthLoginOutput | null): string {
  if (!authContext) {
    return DEFAULT_PROJECT_ID;
  }

  return `project_${sanitizeContextIdPart(authContext.user.user_id)}_creation`;
}

function resolveSessionId(authContext?: AuthLoginOutput | null): string {
  return authContext?.session.session_id ?? DEFAULT_SESSION_ID;
}

export function useProjectSessionContext({
  authContext,
}: UseProjectSessionContextParams) {
  const [projectId, setProjectId] = useState(() => buildProjectId(authContext));
  const [sessionId, setSessionId] = useState(() => resolveSessionId(authContext));

  useEffect(() => {
    setProjectId(buildProjectId(authContext));
    setSessionId(resolveSessionId(authContext));
  }, [authContext]);

  const buildContextOptions: BuildContextOptions = useCallback(
    (sourceStage = "generated_script", requestIdPrefix = "request") =>
      buildCreationContextOptions(
        sourceStage,
        authContext,
        {
          projectId,
          sessionId,
        },
        requestIdPrefix,
      ),
    [authContext, projectId, sessionId],
  );

  return {
    projectId,
    sessionId,
    buildContextOptions,
  };
}
