export type ScriptSourceMode =
  | "idea"
  | "film_script"
  | "novel"
  | "assistant_rewrite"
  | "uploaded_document";

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
