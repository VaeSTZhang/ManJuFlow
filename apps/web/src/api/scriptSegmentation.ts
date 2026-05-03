import type { ExistingScriptInput, ScriptSegmentationOutput } from "../types/scriptSegmentation";

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
    throw new Error("Script segmentation request failed");
  }

  return (await response.json()) as ScriptSegmentationOutput;
}
