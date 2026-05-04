import type { ReactNode } from "react";
import type { AdaptationDraft } from "./creationDraftTypes";

type AdaptationDraftFormProps = {
  isAuthenticated: boolean;
  isFilm: boolean;
  draft: AdaptationDraft;
  documentActionNotice: string;
  documentImportPanel?: ReactNode;
  onChange: <K extends keyof AdaptationDraft>(field: K, value: AdaptationDraft[K]) => void;
  onPendingWordUpload: () => void;
};

export function AdaptationDraftForm({
  isAuthenticated,
  isFilm,
  draft,
  documentActionNotice,
  documentImportPanel,
  onChange,
  onPendingWordUpload,
}: AdaptationDraftFormProps) {
  return (
    <div className="creation-draft-form">
      <section className="document-action-card" aria-label="文档导入与导出">
        <div>
          <h3>Word 文档导入</h3>
          <p>
            上传 Word 后会显示导入预览，确认后可填入下方文本区域。请继续填写“改编方向 /
            重点要求”，让系统知道你希望改成什么短剧方向。
          </p>
        </div>
        <div className="document-action-row">
          <button
            className="secondary-button document-action-button"
            disabled={!isAuthenticated}
            onClick={onPendingWordUpload}
            type="button"
          >
            上传 Word 文档
          </button>
          <button className="secondary-button document-action-button" disabled type="button">
            下载 Word（生成后可用）
          </button>
        </div>
        <p className="document-action-note">支持电影剧本、小说、网文或长文本。导入后请检查文本内容，并补充改编方向。</p>
        {documentActionNotice && <p className="copy-status">{documentActionNotice}</p>}
      </section>

      {documentImportPanel}

      <div className="creation-draft-grid">
        <label className="field creation-draft-field">
          <span>项目标题</span>
          <input
            disabled={!isAuthenticated}
            onChange={(event) => onChange("projectTitle", event.target.value)}
            value={draft.projectTitle}
          />
        </label>
        <label className="field creation-draft-field">
          <span>{isFilm ? "原片 / 原剧本标题" : "原小说 / 文本标题"}</span>
          <input
            disabled={!isAuthenticated}
            onChange={(event) => onChange("sourceTitle", event.target.value)}
            value={draft.sourceTitle}
          />
        </label>
        <label className="field creation-draft-field">
          <span>目标集数</span>
          <input
            disabled={!isAuthenticated}
            min={1}
            onChange={(event) => onChange("episodeCount", Number(event.target.value) || 1)}
            type="number"
            value={draft.episodeCount}
          />
        </label>
      </div>

      <label className="field field-wide creation-draft-field">
        <span>{isFilm ? "原剧本 / 长文本内容" : "小说 / 网文 / 故事文本"}</span>
        <textarea
          disabled={!isAuthenticated}
          onChange={(event) => onChange("sourceText", event.target.value)}
          placeholder={
            isFilm
              ? "上传 Word 后会显示导入预览，确认后可填入这里。也可以直接粘贴电影剧本、长剧本或分场文本。"
              : "上传 Word 后会显示导入预览，确认后可填入这里。也可以直接粘贴小说、网文、故事片段或人物小传。"
          }
          rows={6}
          value={draft.sourceText}
        />
      </label>

      <label className="field field-wide creation-draft-field">
        <span>改编方向 / 重点要求</span>
        <textarea
          disabled={!isAuthenticated}
          onChange={(event) => onChange("focus", event.target.value)}
          placeholder={
            isFilm
              ? "例如：改成 10 集都市复仇短剧；保留原主线，强化反派压迫感；每集结尾增加反转；对白更短剧化。"
              : "例如：突出女主成长线；弱化原作支线；强化家庭伦理冲突；每集设置强钩子；保留核心人物关系。"
          }
          rows={3}
          value={draft.focus}
        />
      </label>

      <label className="field field-wide creation-draft-field">
        <span>额外要求</span>
        <textarea
          disabled={!isAuthenticated}
          onChange={(event) => onChange("extraRequirements", event.target.value)}
          rows={3}
          value={draft.extraRequirements}
        />
      </label>
    </div>
  );
}
