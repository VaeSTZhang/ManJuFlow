import type { ScriptUploadOutput, UploadSourceInput } from "../types/upload";

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
    throw new Error("Script upload mock request failed");
  }

  return (await response.json()) as ScriptUploadOutput;
}
