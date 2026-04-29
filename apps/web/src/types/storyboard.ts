export type StoryboardInput = {
  project_title: string;
  script_text: string;
  episode_number?: number;
  scene_number?: number | null;
  style?: string;
  target_platform?: string;
  visual_style?: string;
  shot_count?: number | null;
  extra_requirements?: string | null;
};

export type StoryboardShot = {
  shot_number: number;
  scene_number: number;
  shot_type: string;
  camera_angle: string;
  camera_movement: string;
  subject: string;
  action: string;
  environment: string;
  lighting: string;
  emotion: string;
  dialogue?: string | null;
  duration_seconds?: number | null;
  visual_notes: string;
  ai_image_prompt_hint?: string | null;
};

export type StoryboardScene = {
  scene_number: number;
  location: string;
  time: string;
  scene_summary: string;
  scene_conflict: string;
  shots: StoryboardShot[];
};

export type StoryboardOutput = {
  project_title: string;
  episode_number: number;
  storyboard_summary: string;
  scenes: StoryboardScene[];
};
