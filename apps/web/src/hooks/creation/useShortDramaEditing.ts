import { useState } from "react";
import type { ShortDramaScriptOutput } from "../../types/scriptGeneration";

function cloneShortDramaScript(script: ShortDramaScriptOutput): ShortDramaScriptOutput {
  return structuredClone(script);
}

export function useShortDramaEditing() {
  const [generatedScript, setGeneratedScript] = useState<ShortDramaScriptOutput | null>(null);
  const [editableScript, setEditableScript] = useState<ShortDramaScriptOutput | null>(null);
  const [isEditingScript, setIsEditingScript] = useState(false);
  const [hasUnsavedScriptEdits, setHasUnsavedScriptEdits] = useState(false);
  const [lastEditedAt, setLastEditedAt] = useState<string | undefined>();
  const effectiveScript = editableScript ?? generatedScript;

  const setGeneratedScriptResult = (result: ShortDramaScriptOutput) => {
    setGeneratedScript(result);
    setEditableScript(null);
    setIsEditingScript(false);
    setHasUnsavedScriptEdits(false);
    setLastEditedAt(undefined);
  };

  const startScriptEditing = () => {
    if (!effectiveScript) {
      return;
    }

    setEditableScript(cloneShortDramaScript(effectiveScript));
    setIsEditingScript(true);
    setHasUnsavedScriptEdits(false);
  };

  const saveScriptEditing = () => {
    setIsEditingScript(false);
    setHasUnsavedScriptEdits(false);
    setLastEditedAt(new Date().toISOString());
  };

  const cancelScriptEditing = () => {
    setEditableScript(null);
    setIsEditingScript(false);
    setHasUnsavedScriptEdits(false);
  };

  const restoreGeneratedScript = () => {
    setEditableScript(null);
    setIsEditingScript(false);
    setHasUnsavedScriptEdits(false);
    setLastEditedAt(undefined);
  };

  return {
    generatedScript,
    editableScript,
    effectiveScript,
    isEditingScript,
    hasUnsavedScriptEdits,
    lastEditedAt,
    setGeneratedScriptResult,
    startScriptEditing,
    saveScriptEditing,
    cancelScriptEditing,
    restoreGeneratedScript,
  };
}
