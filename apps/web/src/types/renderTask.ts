export type RenderTaskItem = {
  task_id: string;
  task_type: string;
  project_title?: string | null;
  prompt_id?: string | null;
  shot_id?: string | null;
  provider: string;
  workflow_name?: string | null;
  status: string;
  progress?: number | null;
  asset_ids: string[];
  error_code?: string | null;
  error_message?: string | null;
  metadata?: Record<string, unknown>;
  created_at?: string | null;
  updated_at?: string | null;
};

export type RenderTaskOutput = {
  project_title: string;
  tasks: RenderTaskItem[];
  metadata?: Record<string, unknown>;
};
