export type DocumentImportMetadataValue = string | number | boolean | null;

export type DocumentImportSource = {
  filename: string;
  content_type?: string | null;
  file_size_bytes?: number | null;
  source_type: string;
  checksum?: string | null;
};

export type DocumentImportPreview = {
  source: DocumentImportSource;
  extracted_text: string;
  preview_text: string;
  character_count: number;
  paragraph_count?: number | null;
  detected_title?: string | null;
  warnings: string[];
  metadata: Record<string, DocumentImportMetadataValue>;
};

export type DocumentImportActionType = "fill" | "append" | "cancel";

export type DocumentImportAction = {
  action: DocumentImportActionType;
  target_field: string;
  imported_text?: string | null;
};

export type DocumentImportStatus = "preview_ready" | "failed" | "rejected";

export type DocumentImportOutput = {
  project_title?: string | null;
  status: DocumentImportStatus;
  preview: DocumentImportPreview;
  next_required_action: string;
};

export type DocumentImportError = {
  error_code: string;
  message: string;
  filename?: string | null;
  details: Record<string, DocumentImportMetadataValue>;
};

export type DocumentImportPreviewRequest = {
  filename: string;
  extracted_text: string;
  content_type?: string | null;
  file_size_bytes?: number | null;
  source_type?: string;
  project_title?: string | null;
  checksum?: string | null;
};
