import type { ScriptUploadOutput, UploadSourceInput } from "../types/upload";
import { createApiErrorFromResponse } from "./errors";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function uploadScriptMock(input: UploadSourceInput): Promise<ScriptUploadOutput> {
  const response = await fetch(`${API_BASE_URL}/api/uploads/script`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "上传 Word 文档 mock 失败，请确认后端服务已启动。");
  }

  return (await response.json()) as ScriptUploadOutput;
}
