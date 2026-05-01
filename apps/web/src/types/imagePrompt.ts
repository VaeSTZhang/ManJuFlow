export type ImagePromptInput = {
  project_title: string;
  storyboard_summary?: string | null;
  storyboard?: Record<string, unknown> | null;
  storyboard_text?: string | null;
  target_model?: string;
  aspect_ratio?: string;
  style_preset?: string;
  language?: string;
  extra_requirements?: string | null;
  llm_provider?: string;
  llm_model?: string;
};

export type ImagePromptItem = {
  prompt_id: string;
  shot_id: string;
  scene_id?: string | null;
  shot_number?: number | null;
  scene_number?: number | null;
  source_visual_description?: string | null;
  positive_prompt: string;
  negative_prompt: string;
  style_preset: string;
  aspect_ratio: string;
  camera_language?: string | null;
  lighting?: string | null;
  color_palette?: string | null;
  character_consistency?: string | null;
  environment?: string | null;
  composition?: string | null;
  model_hint?: string | null;
  seed?: number | null;
  notes?: string | null;
};

export type ImagePromptOutput = {
  project_title: string;
  prompt_summary: string;
  target_model: string;
  aspect_ratio: string;
  style_preset: string;
  items: ImagePromptItem[];
};
