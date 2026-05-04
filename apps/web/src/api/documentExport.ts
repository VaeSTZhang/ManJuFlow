import type {
  DocumentExportFileResponse,
  DocumentExportInput,
  DocumentExportOutput,
} from "../types/documentExport";
import { createApiErrorFromResponse } from "./errors";

const API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_DOCUMENT_EXPORT_FILENAME = "dramora-document.docx";

export function parseFilenameFromContentDisposition(contentDisposition: string | null): string | null {
  if (!contentDisposition) {
    return null;
  }

  const filenameMatch = contentDisposition.match(/filename\*?=(?:UTF-8''|")?([^";]+)"?/i);
  const rawFilename = filenameMatch?.[1]?.trim();

  if (!rawFilename) {
    return null;
  }

  const decodedFilename = decodeURIComponent(rawFilename).replace(/\\/g, "/");
  const safeFilename = decodedFilename.split("/").filter(Boolean).pop()?.trim();
  return safeFilename || null;
}

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

export async function exportDocumentFile(input: DocumentExportInput): Promise<DocumentExportFileResponse> {
  const response = await fetch(`${API_BASE_URL}/api/documents/export-file`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "导出文档失败，请稍后重试或联系技术支持。");
  }

  const blob = await response.blob();
  const filename =
    parseFilenameFromContentDisposition(response.headers.get("content-disposition")) ||
    input.filename ||
    DEFAULT_DOCUMENT_EXPORT_FILENAME;
  const contentType = response.headers.get("content-type") || blob.type;

  return {
    blob,
    filename,
    contentType,
  };
}
