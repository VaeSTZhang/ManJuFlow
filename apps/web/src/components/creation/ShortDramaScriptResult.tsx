import type {
  AdaptationNotes,
  CharacterProfile,
  DialogueLine,
  EpisodeScript,
  SceneScript,
  ScriptSourceMode,
  ShortDramaScriptOutput,
} from "../../types/scriptGeneration";

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

function renderCharacter(character: CharacterProfile) {
  return (
    <article className="short-script-character" key={`${character.name}-${character.role}`}>
      <strong>{character.name}</strong>
      <span>{character.role}</span>
      <p>{character.age}</p>
      <p>{character.personality}</p>
      <small>{character.arc}</small>
    </article>
  );
}

function renderDialogue(dialogue: DialogueLine, index: number) {
  return (
    <p className="short-script-dialogue" key={`${dialogue.character}-${index}`}>
      <strong>{dialogue.character}</strong>
      <span>{dialogue.line}</span>
    </p>
  );
}

function renderScene(scene: SceneScript) {
  return (
    <article className="short-script-scene" key={scene.scene_number}>
      <div className="short-script-scene-header">
        <strong>第 {scene.scene_number} 场</strong>
        <span>
          {scene.location} / {scene.time}
        </span>
      </div>
      <p>{scene.description}</p>
      {scene.dialogues.length > 0 && (
        <div className="short-script-dialogue-list">
          {scene.dialogues.map((dialogue, index) => renderDialogue(dialogue, index))}
        </div>
      )}
      <div className="short-script-scene-notes">
        {scene.visual_notes && <span>画面：{scene.visual_notes}</span>}
        {scene.emotion_curve && <span>情绪：{scene.emotion_curve}</span>}
      </div>
    </article>
  );
}

function renderEpisode(episode: EpisodeScript) {
  return (
    <article className="short-script-episode" key={episode.episode_number}>
      <div className="short-script-episode-header">
        <span>第 {episode.episode_number} 集</span>
        <h3>{episode.title}</h3>
      </div>
      <p>{episode.summary}</p>
      {episode.hook && <strong className="short-script-hook">钩子：{episode.hook}</strong>}
      <div className="short-script-scene-list">{episode.scenes.map(renderScene)}</div>
    </article>
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
  modelLabel = "系统默认模型",
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

  return (
    <section className="short-script-result" aria-label="短剧剧本生成结果">
      <div className="short-script-header">
        <div>
          <span>短剧剧本结果</span>
          <h2>{result.project_title}</h2>
        </div>
        <div className="short-script-actions">
          <button disabled={actionsDisabled || !onCopyJson} onClick={onCopyJson} type="button">
            复制 JSON
          </button>
          <button disabled={actionsDisabled || !onDownloadJson} onClick={onDownloadJson} type="button">
            下载 JSON
          </button>
          <button disabled={actionsDisabled || !onDownloadTxt} onClick={onDownloadTxt} type="button">
            下载 TXT
          </button>
          <button disabled={docxDisabled} onClick={onDownloadDocx} type="button">
            下载 Word
          </button>
          {isEditing ? (
            <>
              <button disabled={actionsDisabled || !onSaveEditing} onClick={onSaveEditing} type="button">
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
            <button disabled={actionsDisabled || !startEditing} onClick={startEditing} type="button">
              开始编辑
            </button>
          )}
        </div>
      </div>

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

      <section className="short-script-section">
        <h3>故事梗概</h3>
        <p>{result.logline}</p>
      </section>

      {result.world_setting && (
        <section className="short-script-section">
          <h3>世界观 / 故事背景</h3>
          <p>{result.world_setting}</p>
        </section>
      )}

      {result.characters.length > 0 && (
        <section className="short-script-section">
          <h3>主要人物</h3>
          <div className="short-script-character-grid">{result.characters.map(renderCharacter)}</div>
        </section>
      )}

      {renderAdaptationNotes(result.adaptation_notes)}

      {result.episodes.length > 0 && (
        <section className="short-script-section">
          <h3>分集内容</h3>
          <div className="short-script-episode-list">{result.episodes.map(renderEpisode)}</div>
        </section>
      )}
    </section>
  );
}
