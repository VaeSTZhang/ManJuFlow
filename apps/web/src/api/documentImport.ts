import type {
  DocumentImportDocxPreviewRequest,
  DocumentImportOutput,
  DocumentImportPreviewRequest,
} from "../types/documentImport";
import { createApiErrorFromResponse } from "./errors";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function previewDocumentImport(
  input: DocumentImportPreviewRequest,
): Promise<DocumentImportOutput> {
  const response = await fetch(`${API_BASE_URL}/api/documents/import-preview`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "生成文档导入预览失败，请确认服务已启动。");
  }

  return (await response.json()) as DocumentImportOutput;
}

function appendOptionalFormValue(formData: FormData, key: string, value: string | null | undefined) {
  if (value !== null && value !== undefined && value !== "") {
    formData.append(key, value);
  }
}

export async function previewDocxDocumentImport(
  input: DocumentImportDocxPreviewRequest,
): Promise<DocumentImportOutput> {
  const formData = new FormData();
  formData.append("file", input.file);
  appendOptionalFormValue(formData, "project_title", input.project_title);

  const contextOptions = input.context_options;
  appendOptionalFormValue(formData, "user_id", contextOptions?.user_id);
  appendOptionalFormValue(formData, "workspace_id", contextOptions?.workspace_id);
  appendOptionalFormValue(formData, "project_id", contextOptions?.project_id);
  appendOptionalFormValue(formData, "session_id", contextOptions?.session_id);
  appendOptionalFormValue(formData, "request_id", contextOptions?.request_id);
  appendOptionalFormValue(formData, "source_stage", contextOptions?.source_stage ?? "imported_document");
  appendOptionalFormValue(formData, "context_policy", contextOptions?.context_policy ?? "current_project_only");

  const response = await fetch(`${API_BASE_URL}/api/documents/import-docx-preview`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "生成 Word 文档导入预览失败，请稍后重试。");
  }

  return (await response.json()) as DocumentImportOutput;
}
