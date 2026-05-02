export type AssetItem = {
  asset_id: string;
  asset_type: string;
  project_title?: string | null;
  prompt_id?: string | null;
  shot_id?: string | null;
  task_id?: string | null;
  provider: string;
  status: string;
  url?: string | null;
  mock_url?: string | null;
  local_path?: string | null;
  width?: number | null;
  height?: number | null;
  seed?: number | null;
  metadata?: Record<string, unknown>;
  created_at?: string | null;
  notes?: string | null;
};

export type AssetCollection = {
  project_title: string;
  assets: AssetItem[];
  metadata?: Record<string, unknown>;
};
