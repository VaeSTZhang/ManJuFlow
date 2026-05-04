import { useState } from "react";
import type { DocumentImportOutput } from "../../types/documentImport";

export type DocumentImportAdaptationMode = "film" | "novel";

export type DocumentImportDraftState = {
  filename: string;
  text: string;
  preview: DocumentImportOutput | null;
  error: string;
  isLoading: boolean;
};

type DocumentImportDraftsByMode = Record<DocumentImportAdaptationMode, DocumentImportDraftState>;

const defaultDocumentImportDraftState: DocumentImportDraftState = {
  filename: "",
  text: "",
  preview: null,
  error: "",
  isLoading: false,
};

const defaultDocumentImportDrafts: DocumentImportDraftsByMode = {
  film: { ...defaultDocumentImportDraftState },
  novel: { ...defaultDocumentImportDraftState },
};

export function useDocumentImportDrafts() {
  const [documentImportDrafts, setDocumentImportDrafts] =
    useState<DocumentImportDraftsByMode>(defaultDocumentImportDrafts);

  const updateDocumentImportDraft = (
    mode: DocumentImportAdaptationMode,
    patch: Partial<DocumentImportDraftState>,
  ) => {
    setDocumentImportDrafts((current) => ({
      ...current,
      [mode]: {
        ...current[mode],
        ...patch,
      },
    }));
  };

  const clearDocumentImportPreview = (mode: DocumentImportAdaptationMode) => {
    updateDocumentImportDraft(mode, {
      preview: null,
      error: "",
    });
  };

  return {
    documentImportDrafts,
    updateDocumentImportDraft,
    clearDocumentImportPreview,
  };
}
