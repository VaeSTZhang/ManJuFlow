export type ScriptSourceMode =
  | "idea"
  | "film_script"
  | "novel"
  | "assistant_rewrite"
  | "uploaded_document";

export type AIRequestPurpose =
  | "script_generation"
  | "film_adaptation"
  | "novel_adaptation"
  | "assistant_chat"
  | "script_rewrite"
  | "quality_review"
  | "storyboard_generation"
  | "prompt_generation";

export type AIRequestOptions = {
  provider?: string | null;
  model?: string | null;
  temperature?: number | null;
  max_tokens?: number | null;
  language: string;
  purpose: AIRequestPurpose;
};

export type ContextOptions = {
  user_id?: string | null;
  workspace_id?: string | null;
  project_id?: string | null;
  session_id?: string | null;
  request_id?: string | null;
  source_stage?: string | null;
  context_policy?: string;
};

export type ShortDramaGenerationInput = {
  project_title?: string | null;
  source_mode: ScriptSourceMode;
  idea_text?: string | null;
  source_text?: string | null;
  target_episode_count: number;
  genre: string;
  style: string;
  target_audience?: string | null;
  duration_per_episode?: string | null;
  adaptation_goal?: string | null;
  key_plot_must_keep?: string | null;
  main_characters?: string | null;
  key_relationships?: string | null;
  extra_requirements?: string | null;
  language: string;
  workspace_id?: string | null;
  project_id?: string | null;
  session_id?: string | null;
  user_id?: string | null;
  ai_options?: AIRequestOptions | null;
  context_options?: ContextOptions | null;
  metadata?: Record<string, unknown>;
};

export type CharacterProfile = {
  name: string;
  role: string;
  age: string;
  personality: string;
  arc: string;
};

export type DialogueLine = {
  character: string;
  line: string;
};

export type SceneScript = {
  scene_number: number;
  location: string;
  time: string;
  description: string;
  dialogues: DialogueLine[];
  visual_notes: string;
  emotion_curve: string;
};

export type EpisodeScript = {
  episode_number: number;
  title: string;
  summary: string;
  hook: string;
  scenes: SceneScript[];
};

export type AdaptationNotes = {
  source_mode: ScriptSourceMode;
  adaptation_strategy?: string | null;
  preserved_elements: string[];
  changed_elements: string[];
  short_drama_hooks: string[];
  risk_notes: string[];
};

export type ShortDramaScriptOutput = {
  project_title: string;
  source_mode: ScriptSourceMode;
  logline: string;
  world_setting: string;
  characters: CharacterProfile[];
  adaptation_notes?: AdaptationNotes | null;
  episode_count: number;
  episodes: EpisodeScript[];
  metadata: Record<string, unknown>;
};
