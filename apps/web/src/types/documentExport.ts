export type DocumentExportFormat = "txt" | "json" | "docx";

export type DocumentSourceStage =
  | "script"
  | "script_segmentation"
  | "storyboard"
  | "image_prompt"
  | "assistant"
  | "other";

export type DocumentExportMetadataValue = string | number | boolean | null;

export type DocumentExportInput = {
  project_title: string;
  document_type?: string;
  source_stage?: DocumentSourceStage;
  content_text?: string | null;
  structured_payload?: Record<string, unknown> | null;
  export_format: DocumentExportFormat;
  filename?: string | null;
  workspace_id?: string | null;
  project_id?: string | null;
  session_id?: string | null;
  metadata?: Record<string, DocumentExportMetadataValue>;
};

export type DocumentExportOutput = {
  project_title: string;
  document_type: string;
  source_stage: DocumentSourceStage;
  export_format: DocumentExportFormat;
  filename: string;
  content_text?: string | null;
  download_url?: string | null;
  file_size_bytes?: number | null;
  workspace_id?: string | null;
  project_id?: string | null;
  session_id?: string | null;
  metadata: Record<string, DocumentExportMetadataValue>;
};

export type DocumentExportFileResponse = {
  blob: Blob;
  filename: string;
  contentType: string;
};
