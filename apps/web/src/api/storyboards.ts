import type { StoryboardInput, StoryboardOutput } from "../types/storyboard";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function generateStoryboard(input: StoryboardInput): Promise<StoryboardOutput> {
  const response = await fetch(`${API_BASE_URL}/api/storyboards/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw new Error("Storyboard generation request failed");
  }

  return (await response.json()) as StoryboardOutput;
}
