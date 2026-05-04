import type { ShortDramaGenerationInput, ShortDramaScriptOutput } from "../types/scriptGeneration";
import { createApiErrorFromResponse } from "./errors";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function generateShortDramaScript(
  input: ShortDramaGenerationInput,
): Promise<ShortDramaScriptOutput> {
  const response = await fetch(`${API_BASE_URL}/api/scripts/generate-from-source`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw await createApiErrorFromResponse(response, "生成短剧剧本失败，请确认后端服务已启动。");
  }

  return (await response.json()) as ShortDramaScriptOutput;
}
