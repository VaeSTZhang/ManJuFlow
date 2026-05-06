import { previewDocumentImport, previewDocxDocumentImport } from "../../api/documentImport";
import { parseApiErrorMessage } from "../../api/errors";
import type {
  AdaptationDraft,
  AdaptationMode,
  CreationDrafts,
} from "../../components/creation/creationDraftTypes";
import { buildCreationContextOptions } from "../../utils/contextOptions";
import type { DocumentImportDraftState } from "./useDocumentImportDrafts";

type UpdateDocumentImportDraft = (
  mode: AdaptationMode,
  patch: Partial<DocumentImportDraftState>,
) => void;

type ClearDocumentImportPreview = (mode: AdaptationMode) => void;

type UpdateAdaptationDraft = <K extends keyof AdaptationDraft>(
  mode: AdaptationMode,
  field: K,
  value: AdaptationDraft[K],
) => void;

type UseDocumentImportPreviewParams = {
  isAuthenticated: boolean;
  onRequireLogin: () => void;
  drafts: CreationDrafts;
  documentImportDrafts: Record<AdaptationMode, DocumentImportDraftState>;
  updateDocumentImportDraft: UpdateDocumentImportDraft;
  clearDocumentImportPreview: ClearDocumentImportPreview;
  updateAdaptationDraft: UpdateAdaptationDraft;
};

function getImportProjectTitle(draft: AdaptationDraft): string | null {
  return draft.projectTitle.trim() || draft.sourceTitle.trim() || null;
}

export function useDocumentImportPreview({
  isAuthenticated,
  onRequireLogin,
  drafts,
  documentImportDrafts,
  updateDocumentImportDraft,
  clearDocumentImportPreview,
  updateAdaptationDraft,
}: UseDocumentImportPreviewParams) {
  const handleGenerateDocumentImportPreview = async (mode: AdaptationMode) => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    const importDraft = documentImportDrafts[mode];
    const filename = importDraft.filename.trim();
    const extractedText = importDraft.text.trim();

    if (!filename) {
      updateDocumentImportDraft(mode, { error: "请先填写文件名。" });
      return;
    }

    if (!extractedText) {
      updateDocumentImportDraft(mode, { error: "请先粘贴文档文本。" });
      return;
    }

    const draft = drafts[mode];
    updateDocumentImportDraft(mode, {
      isLoading: true,
      error: "",
    });

    try {
      const preview = await previewDocumentImport({
        filename,
        extracted_text: extractedText,
        source_type: mode === "novel" ? "novel" : "docx",
        project_title: getImportProjectTitle(draft),
        context_options: buildCreationContextOptions("imported_document"),
      });
      updateDocumentImportDraft(mode, { preview });
    } catch (error) {
      updateDocumentImportDraft(mode, {
        error: parseApiErrorMessage(
          error,
          "生成文档导入预览失败，请确认服务已启动。",
        ),
      });
    } finally {
      updateDocumentImportDraft(mode, { isLoading: false });
    }
  };

  const handleGenerateDocxDocumentImportPreview = async (mode: AdaptationMode, file: File) => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    const draft = drafts[mode];
    updateDocumentImportDraft(mode, {
      isLoading: true,
      error: "",
    });

    try {
      const preview = await previewDocxDocumentImport({
        file,
        project_title: getImportProjectTitle(draft),
        context_options: buildCreationContextOptions("imported_document"),
      });
      updateDocumentImportDraft(mode, {
        filename: preview.preview.source.filename,
        preview,
      });
    } catch (error) {
      updateDocumentImportDraft(mode, {
        error: parseApiErrorMessage(
          error,
          "生成 Word 文档导入预览失败，请稍后重试。",
        ),
      });
    } finally {
      updateDocumentImportDraft(mode, { isLoading: false });
    }
  };

  const applyDocumentImportPreview = (mode: AdaptationMode, action: "fill" | "append" | "cancel") => {
    if (action === "cancel") {
      clearDocumentImportPreview(mode);
      return;
    }

    const importDraft = documentImportDrafts[mode];

    if (!importDraft.preview) {
      return;
    }

    const importedText = importDraft.preview.preview.extracted_text;

    updateAdaptationDraft(
      mode,
      "sourceText",
      action === "fill"
        ? importedText
        : [drafts[mode].sourceText.trim(), importedText].filter(Boolean).join("\n\n"),
    );
    clearDocumentImportPreview(mode);
  };

  return {
    handleGenerateDocumentImportPreview,
    handleGenerateDocxDocumentImportPreview,
    applyDocumentImportPreview,
  };
}
