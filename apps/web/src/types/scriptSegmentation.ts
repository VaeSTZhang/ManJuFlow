export type ExistingScriptInput = {
  project_title: string;
  script_text?: string | null;
  source_id?: string | null;
  source_type?: string;
  target_segment_level?: string;
  language?: string;
  extra_requirements?: string | null;
  workspace_id?: string | null;
  user_id?: string | null;
  ai_account_id?: string | null;
  metadata?: Record<string, unknown>;
};

export type ScriptSegment = {
  segment_id: string;
  episode_number?: number | null;
  scene_number?: number | null;
  segment_type: string;
  title: string;
  original_text: string;
  summary: string;
  characters: string[];
  location?: string | null;
  time_of_day?: string | null;
  conflict?: string | null;
  emotion?: string | null;
  visual_notes?: string | null;
  dialogue_text?: string | null;
  estimated_duration_seconds?: number | null;
  next_step_hint?: string | null;
  metadata?: Record<string, unknown>;
};

export type ScriptSegmentationOutput = {
  project_title: string;
  segmentation_summary: string;
  segment_count: number;
  segments: ScriptSegment[];
  source_id?: string | null;
  workspace_id?: string | null;
  user_id?: string | null;
  ai_account_id?: string | null;
  metadata?: Record<string, unknown>;
};
