import type { ExistingScriptInput, ScriptSegmentationOutput } from "../types/scriptSegmentation";
import { createApiErrorFromResponse } from "./errors";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function segmentScript(input: ExistingScriptInput): Promise<ScriptSegmentationOutput> {
  const response = await fetch(`${API_BASE_URL}/api/scripts/segment`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "切分已有剧本失败，请确认后端服务已启动。");
  }

  return (await response.json()) as ScriptSegmentationOutput;
}
