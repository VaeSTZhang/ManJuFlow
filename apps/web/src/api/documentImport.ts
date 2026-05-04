import type { DocumentImportOutput, DocumentImportPreviewRequest } from "../types/documentImport";
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
