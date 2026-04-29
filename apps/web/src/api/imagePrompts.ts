import type { ImagePromptInput, ImagePromptOutput } from "../types/imagePrompt";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function generateImagePrompts(input: ImagePromptInput): Promise<ImagePromptOutput> {
  const response = await fetch(`${API_BASE_URL}/api/prompts/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw new Error("Image prompt generation request failed");
  }

  return (await response.json()) as ImagePromptOutput;
}
