import type {
  AdaptationNotes,
  CharacterProfile,
  ScriptSourceMode,
  ShortDramaScriptOutput,
} from "../../types/scriptGeneration";
import { ShortDramaBasicInfoEditor } from "./ShortDramaBasicInfoEditor";
import { ShortDramaCharacterEditor } from "./ShortDramaCharacterEditor";
import {
  ShortDramaEpisodeEditor,
  type EditableEpisodeField,
} from "./ShortDramaEpisodeEditor";

type ShortDramaScriptResultProps = {
  result: ShortDramaScriptOutput | null;
  sourceLabel?: string;
  modelLabel?: string;
  generatedAt?: string;
  isLocked?: boolean;
  isEditing?: boolean;
  isEditedDraft?: boolean;
  hasUnsavedEdits?: boolean;
  lastEditedAt?: string;
  onCopyJson?: () => void;
  onDownloadJson?: () => void;
  onDownloadTxt?: () => void;
  onDownloadDocx?: () => void;
  onEdit?: () => void;
  onStartEditing?: () => void;
  onSaveEditing?: () => void;
  onCancelEditing?: () => void;
  onRestoreGenerated?: () => void;
  onUpdateField?: <K extends keyof ShortDramaScriptOutput>(
    field: K,
    value: ShortDramaScriptOutput[K],
  ) => void;
  onUpdateCharacterField?: (
    characterIndex: number,
    field: keyof CharacterProfile,
    value: string,
  ) => void;
  onUpdateEpisodeField?: (
    episodeIndex: number,
    field: EditableEpisodeField,
    value: string,
  ) => void;
};

const sourceModeLabels: Record<ScriptSourceMode, string> = {
  idea: "灵感生成",
  film_script: "电影剧本改编",
  novel: "小说改编",
  assistant_rewrite: "AI 助手改写",
  uploaded_document: "上传文档",
};

function resolveSourceLabel(result: ShortDramaScriptOutput, sourceLabel?: string): string {
  return sourceLabel ?? sourceModeLabels[result.source_mode] ?? "系统默认";
}

function renderTextList(title: string, items: string[]) {
  const visibleItems = items.filter((item) => item.trim() !== "");

  if (visibleItems.length === 0) {
    return null;
  }

  return (
    <section className="short-script-section">
      <h3>{title}</h3>
      <ul className="short-script-note-list">
        {visibleItems.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

function renderAdaptationNotes(notes?: AdaptationNotes | null) {
  if (!notes) {
    return null;
  }

  return (
    <>
      {notes.adaptation_strategy && (
        <section className="short-script-section">
          <h3>改编策略</h3>
          <p>{notes.adaptation_strategy}</p>
        </section>
      )}
      {renderTextList("保留元素", notes.preserved_elements)}
      {renderTextList("调整内容", notes.changed_elements)}
      {renderTextList("短剧钩子 / 爆点", notes.short_drama_hooks)}
      {renderTextList("备注", notes.risk_notes)}
    </>
  );
}

export function ShortDramaScriptResult({
  result,
  sourceLabel,
  modelLabel = "当前创作模型",
  generatedAt,
  isLocked = false,
  isEditing = false,
  isEditedDraft = false,
  hasUnsavedEdits = false,
  lastEditedAt,
  onCopyJson,
  onDownloadJson,
  onDownloadTxt,
  onDownloadDocx,
  onEdit,
  onStartEditing,
  onSaveEditing,
  onCancelEditing,
  onRestoreGenerated,
  onUpdateField,
  onUpdateCharacterField,
  onUpdateEpisodeField,
}: ShortDramaScriptResultProps) {
  if (!result) {
    return (
      <section className="short-script-result short-script-empty" aria-label="短剧剧本生成结果">
        <div>
          <span>短剧剧本结果</span>
          <h2>生成结果将在这里展示</h2>
          <p>请选择创作方式并生成短剧剧本</p>
        </div>
      </section>
    );
  }

  const actionsDisabled = isLocked;
  const docxDisabled = isLocked || !onDownloadDocx;
  const startEditing = onStartEditing ?? onEdit;
  const canEditFields = isEditing && !!onUpdateField && !isLocked;
  const resultActions = (
    <div className="short-script-actions">
      <button
        data-testid="copy-script-json"
        disabled={actionsDisabled || !onCopyJson}
        onClick={onCopyJson}
        type="button"
      >
        复制 JSON
      </button>
      <button
        data-testid="download-script-json"
        disabled={actionsDisabled || !onDownloadJson}
        onClick={onDownloadJson}
        type="button"
      >
        下载 JSON
      </button>
      <button
        data-testid="download-script-txt"
        disabled={actionsDisabled || !onDownloadTxt}
        onClick={onDownloadTxt}
        type="button"
      >
        下载 TXT
      </button>
      <button disabled={docxDisabled} onClick={onDownloadDocx} type="button">
        下载 Word
      </button>
      {isEditing ? (
        <>
          <button
            data-testid="save-script-editing"
            disabled={actionsDisabled || !onSaveEditing}
            onClick={onSaveEditing}
            type="button"
          >
            保存本次修改
          </button>
          <button disabled={actionsDisabled || !onCancelEditing} onClick={onCancelEditing} type="button">
            放弃修改
          </button>
          <button disabled={actionsDisabled || !onRestoreGenerated} onClick={onRestoreGenerated} type="button">
            恢复为 AI 原始结果
          </button>
        </>
      ) : (
        <button
          data-testid="start-script-editing"
          disabled={actionsDisabled || !startEditing}
          onClick={startEditing}
          type="button"
        >
          开始编辑
        </button>
      )}
    </div>
  );
  const resultMetaAndNotes = (
    <>
      <div className="short-script-meta">
        <span>来源入口：{resolveSourceLabel(result, sourceLabel)}</span>
        <span>使用模型：{modelLabel}</span>
        <span>生成时间：{generatedAt ?? "生成后显示"}</span>
        <span>当前展示：{isEditedDraft ? "编辑稿" : "AI 原始稿"}</span>
        {lastEditedAt && <span>上次编辑：{lastEditedAt}</span>}
        <span>集数：{result.episode_count}</span>
      </div>

      {isLocked && <p className="short-script-action-note">登录后可导出生成结果</p>}
      {hasUnsavedEdits && <p className="short-script-action-note">当前有未保存修改</p>}
      {!onDownloadDocx && <p className="short-script-action-note">Word 导出将在文档导出闭环接入</p>}
    </>
  );

  return (
    <section className="short-script-result" aria-label="短剧剧本生成结果" data-testid="short-drama-script-result">
      <ShortDramaBasicInfoEditor
        actions={resultActions}
        afterHeader={resultMetaAndNotes}
        canEditFields={canEditFields}
        onUpdateField={onUpdateField}
        result={result}
      />

      <ShortDramaCharacterEditor
        canEditFields={canEditFields}
        characters={result.characters}
        onUpdateCharacterField={onUpdateCharacterField}
      />

      {renderAdaptationNotes(result.adaptation_notes)}

      <ShortDramaEpisodeEditor
        canEditFields={canEditFields}
        episodes={result.episodes}
        onUpdateEpisodeField={onUpdateEpisodeField}
      />
    </section>
  );
}
