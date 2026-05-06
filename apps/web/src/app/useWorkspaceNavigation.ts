import { useState } from "react";

type UseWorkspaceNavigationParams = {
  isAuthenticated: boolean;
  onRequireLogin: () => void;
};

const DEFAULT_WORKSPACE_ID = "creation-home";

export function useWorkspaceNavigation({
  isAuthenticated,
  onRequireLogin: _onRequireLogin,
}: UseWorkspaceNavigationParams) {
  const [activeWorkspaceId, setActiveWorkspaceId] = useState(DEFAULT_WORKSPACE_ID);
  const isBrowsingMode = !isAuthenticated;

  const handleWorkspaceChange = (workspaceId: string) => {
    setActiveWorkspaceId(workspaceId);
  };

  return {
    activeWorkspaceId,
    setActiveWorkspaceId,
    handleWorkspaceChange,
    isBrowsingMode,
  };
}
