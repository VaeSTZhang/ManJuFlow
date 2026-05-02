export type ImageGenerationPromptItem = {
  prompt_id: string;
  shot_id: string;
  positive_prompt: string;
  negative_prompt: string;
  style_preset?: string;
  aspect_ratio?: string;
  model_hint?: string | null;
  seed?: number | null;
  metadata?: Record<string, unknown>;
};

export type ImageGenerationInput = {
  project_title: string;
  prompt_items: ImageGenerationPromptItem[];
  provider?: string;
  workflow_name?: string;
  style_preset?: string;
  aspect_ratio?: string;
  output_count?: number;
  seed?: number | null;
  extra_parameters?: Record<string, unknown>;
};

export type ImageGenerationItem = {
  task_id: string;
  prompt_id: string;
  shot_id: string;
  status: string;
  positive_prompt: string;
  negative_prompt: string;
  provider: string;
  workflow_name: string;
  image_url?: string | null;
  mock_url?: string | null;
  local_path?: string | null;
  width?: number | null;
  height?: number | null;
  seed?: number | null;
  metadata?: Record<string, unknown>;
  error_message?: string | null;
};

export type ImageGenerationOutput = {
  project_title: string;
  provider: string;
  status: string;
  items: ImageGenerationItem[];
  metadata?: Record<string, unknown>;
};
