import type { DocumentExportInput, DocumentExportOutput } from "../types/documentExport";
import { createApiErrorFromResponse } from "./errors";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function exportDocument(input: DocumentExportInput): Promise<DocumentExportOutput> {
  const response = await fetch(`${API_BASE_URL}/api/documents/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "导出文档失败，请稍后重试或联系技术支持。");
  }

  return (await response.json()) as DocumentExportOutput;
}
