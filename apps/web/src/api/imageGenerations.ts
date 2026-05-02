import type { ImageGenerationInput, ImageGenerationOutput } from "../types/imageGeneration";
import type { ImageGenerationBundleOutput } from "../types/imageGenerationBundle";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function generateImages(input: ImageGenerationInput): Promise<ImageGenerationOutput> {
  const response = await fetch(`${API_BASE_URL}/api/images/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw new Error("Image generation request failed");
  }

  return (await response.json()) as ImageGenerationOutput;
}

export async function generateImageBundle(input: ImageGenerationInput): Promise<ImageGenerationBundleOutput> {
  const response = await fetch(`${API_BASE_URL}/api/images/generate-bundle`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw new Error("Image generation bundle request failed");
  }

  return (await response.json()) as ImageGenerationBundleOutput;
}
