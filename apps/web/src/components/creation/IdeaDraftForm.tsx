import type { IdeaCreationDraft } from "./creationDraftTypes";

type IdeaDraftFormProps = {
  isAuthenticated: boolean;
  draft: IdeaCreationDraft;
  onChange: <K extends keyof IdeaCreationDraft>(field: K, value: IdeaCreationDraft[K]) => void;
};

export function IdeaDraftForm({ isAuthenticated, draft, onChange }: IdeaDraftFormProps) {
  return (
    <div className="creation-draft-form">
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
          <span>类型 / 风格</span>
          <input
            disabled={!isAuthenticated}
            onChange={(event) => onChange("genreStyle", event.target.value)}
            value={draft.genreStyle}
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
        <span>灵感内容</span>
        <textarea
          disabled={!isAuthenticated}
          onChange={(event) => onChange("ideaText", event.target.value)}
          placeholder="例如：一个失意编剧在旧电影院发现父亲留下的未完成剧本，每一页都指向一段被隐藏的真相。"
          rows={5}
          value={draft.ideaText}
        />
      </label>

      <label className="field field-wide creation-draft-field">
        <span>额外要求</span>
        <textarea
          disabled={!isAuthenticated}
          onChange={(event) => onChange("extraRequirements", event.target.value)}
          placeholder="例如：节奏更紧，前 30 秒必须有强钩子，每集结尾留反转。"
          rows={3}
          value={draft.extraRequirements}
        />
      </label>
    </div>
  );
}
