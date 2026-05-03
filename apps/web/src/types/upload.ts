export type UploadSourceInput = {
  project_title: string;
  source_type?: string;
  workspace_id?: string | null;
  project_id?: string | null;
  user_id?: string | null;
  ai_account_id?: string | null;
  language?: string;
  extra_requirements?: string | null;
  metadata?: Record<string, unknown>;
};

export type UploadSourceMetadata = {
  source_id: string;
  project_title: string;
  project_id?: string | null;
  workspace_id?: string | null;
  user_id?: string | null;
  ai_account_id?: string | null;
  original_filename: string;
  content_type: string;
  file_size: number;
  sha256?: string | null;
  storage_path?: string | null;
  source_type: string;
  extraction_status: string;
  extracted_text_length: number;
  created_at?: string | null;
  metadata?: Record<string, unknown>;
};

export type ScriptUploadOutput = {
  source_id: string;
  project_title: string;
  extracted_text: string;
  metadata: UploadSourceMetadata;
  warnings: string[];
};

export type UploadError = {
  error_code: string;
  message: string;
  detail?: string | null;
  metadata?: Record<string, unknown>;
};
