import { useState } from "react";
import type { DocumentImportOutput } from "../../types/documentImport";

type DocumentImportPanelProps = {
  isAuthenticated: boolean;
  isFilm: boolean;
  filename: string;
  text: string;
  preview: DocumentImportOutput | null;
  error: string;
  isLoading: boolean;
  onFilenameChange: (value: string) => void;
  onTextChange: (value: string) => void;
  onGeneratePreview: () => void;
  onGenerateDocxPreview: (file: File) => void;
  onApplyFill: () => void;
  onApplyAppend: () => void;
  onCancel: () => void;
};

export function DocumentImportPanel({
  isAuthenticated,
  isFilm,
  filename,
  text,
  preview,
  error,
  isLoading,
  onFilenameChange,
  onTextChange,
  onGeneratePreview,
  onGenerateDocxPreview,
  onApplyFill,
  onApplyAppend,
  onCancel,
}: DocumentImportPanelProps) {
  const [selectedDocxFile, setSelectedDocxFile] = useState<File | null>(null);

  return (
    <section className="document-import-panel" aria-label="文档导入预览" data-testid="document-import-panel">
      <div>
        <h3>导入剧本文档内容</h3>
        <p>上传或粘贴文档内容生成预览，确认后再填入待改编文本。系统不会自动决定改编方向。</p>
      </div>

      <div className="document-import-grid">
        <label className="field creation-draft-field">
          <span>上传 Word 文档</span>
          <input
            accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            data-testid="docx-import-file-input"
            disabled={!isAuthenticated || isLoading}
            onChange={(event) => setSelectedDocxFile(event.target.files?.[0] ?? null)}
            type="file"
          />
        </label>
        <div className="document-import-upload-action">
          <p>选择 .docx 文件生成导入预览。上传后请确认填入、追加或取消，系统不会自动决定改编方向。</p>
          <button
            className="secondary-button"
            data-testid="generate-docx-import-preview"
            disabled={!isAuthenticated || isLoading || !selectedDocxFile}
            onClick={() => {
              if (selectedDocxFile) {
                onGenerateDocxPreview(selectedDocxFile);
              }
            }}
            type="button"
          >
            {isLoading ? "生成预览中..." : "上传 Word 文档"}
          </button>
        </div>
      </div>

      <div className="document-import-grid">
        <label className="field creation-draft-field">
          <span>文件名</span>
          <input
            disabled={!isAuthenticated || isLoading}
            onChange={(event) => onFilenameChange(event.target.value)}
            placeholder={isFilm ? "example-film-script.docx" : "example-novel.docx"}
            value={filename}
          />
        </label>
        <label className="field creation-draft-field">
          <span>文档文本</span>
          <textarea
            disabled={!isAuthenticated || isLoading}
            onChange={(event) => onTextChange(event.target.value)}
            placeholder={
              isFilm
                ? "粘贴电影剧本、长剧本或分场文本，生成预览后再确认填入。"
                : "粘贴小说、网文、故事片段或人物小传，生成预览后再确认填入。"
            }
            rows={5}
            value={text}
          />
        </label>
      </div>

      <div className="document-import-actions">
        <button
          className="secondary-button"
          disabled={!isAuthenticated || isLoading}
          onClick={onGeneratePreview}
          type="button"
        >
          {isLoading ? "生成预览中..." : "生成导入预览"}
        </button>
      </div>

      {error && <p className="form-error">{error}</p>}

      {preview && (
        <article className="document-import-preview">
          <div className="document-import-preview-header">
            <div>
              <span>文档导入预览</span>
              <strong>{preview.preview.detected_title || "未识别标题"}</strong>
            </div>
            <small>{preview.preview.source.filename}</small>
          </div>

          <dl className="document-import-preview-meta">
            <div>
              <dt>字数</dt>
              <dd>{preview.preview.character_count}</dd>
            </div>
            <div>
              <dt>段落数</dt>
              <dd>{preview.preview.paragraph_count ?? 0}</dd>
            </div>
          </dl>

          {preview.preview.warnings.length > 0 && (
            <div className="document-import-warning">
              {preview.preview.warnings.map((warning) => (
                <p key={warning}>{warning}</p>
              ))}
            </div>
          )}

          <p className="document-import-preview-text">{preview.preview.preview_text}</p>

          <div className="document-import-actions">
            <button className="primary-button" disabled={!isAuthenticated} onClick={onApplyFill} type="button">
              填入待改编文本
            </button>
            <button className="secondary-button" disabled={!isAuthenticated} onClick={onApplyAppend} type="button">
              追加到当前文本后
            </button>
            <button className="secondary-button" disabled={!isAuthenticated} onClick={onCancel} type="button">
              取消导入
            </button>
          </div>
        </article>
      )}
    </section>
  );
}
