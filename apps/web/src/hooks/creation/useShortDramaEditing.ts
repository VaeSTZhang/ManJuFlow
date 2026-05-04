import { useState } from "react";
import type { CharacterProfile, ShortDramaScriptOutput } from "../../types/scriptGeneration";

type EditableEpisodeField = "title" | "summary" | "hook";

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

  const updateEditableScriptField = <K extends keyof ShortDramaScriptOutput>(
    field: K,
    value: ShortDramaScriptOutput[K],
  ) => {
    setEditableScript((currentEditableScript) => {
      const baseScript = currentEditableScript ?? generatedScript;

      if (!baseScript) {
        return currentEditableScript;
      }

      return {
        ...cloneShortDramaScript(baseScript),
        [field]: value,
      };
    });
    setHasUnsavedScriptEdits(true);
  };

  const updateEditableCharacterField = (
    characterIndex: number,
    field: keyof CharacterProfile,
    value: string,
  ) => {
    setEditableScript((currentEditableScript) => {
      const baseScript = currentEditableScript ?? generatedScript;

      if (!baseScript || !baseScript.characters[characterIndex]) {
        return currentEditableScript;
      }

      const nextScript = cloneShortDramaScript(baseScript);
      nextScript.characters[characterIndex] = {
        ...nextScript.characters[characterIndex],
        [field]: value,
      };

      return nextScript;
    });
    setHasUnsavedScriptEdits(true);
  };

  const updateEditableEpisodeField = (
    episodeIndex: number,
    field: EditableEpisodeField,
    value: string,
  ) => {
    setEditableScript((currentEditableScript) => {
      const baseScript = currentEditableScript ?? generatedScript;

      if (!baseScript || !baseScript.episodes[episodeIndex]) {
        return currentEditableScript;
      }

      const nextScript = cloneShortDramaScript(baseScript);
      nextScript.episodes[episodeIndex] = {
        ...nextScript.episodes[episodeIndex],
        [field]: value,
      };

      return nextScript;
    });
    setHasUnsavedScriptEdits(true);
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
    updateEditableScriptField,
    updateEditableCharacterField,
    updateEditableEpisodeField,
  };
}
