import type { DialogueLine, EpisodeScript, SceneScript } from "../../types/scriptGeneration";

export type EditableEpisodeField = "title" | "summary" | "hook";

type ShortDramaEpisodeEditorProps = {
  episodes: EpisodeScript[];
  canEditFields?: boolean;
  onUpdateEpisodeField?: (
    episodeIndex: number,
    field: EditableEpisodeField,
    value: string,
  ) => void;
};

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

function renderEpisode(
  episode: EpisodeScript,
  index: number,
  canEditFields: boolean,
  onUpdateEpisodeField?: (
    episodeIndex: number,
    field: EditableEpisodeField,
    value: string,
  ) => void,
) {
  const canEditEpisode = canEditFields && !!onUpdateEpisodeField;

  return (
    <article className="short-script-episode" key={episode.episode_number}>
      <div className="short-script-episode-header">
        <span>第 {episode.episode_number} 集</span>
        {canEditEpisode ? (
          <label className="short-script-edit-field">
            <span>分集标题</span>
            <input
              data-testid={`episode-title-editor-${index}`}
              onChange={(event) => onUpdateEpisodeField(index, "title", event.target.value)}
              value={episode.title}
            />
          </label>
        ) : (
          <h3>{episode.title}</h3>
        )}
      </div>
      {canEditEpisode ? (
        <label className="short-script-edit-field">
          <span>分集概要</span>
          <textarea
            data-testid={`episode-summary-editor-${index}`}
            onChange={(event) => onUpdateEpisodeField(index, "summary", event.target.value)}
            rows={3}
            value={episode.summary}
          />
        </label>
      ) : (
        <p>{episode.summary}</p>
      )}
      {canEditEpisode ? (
        <label className="short-script-edit-field">
          <span>分集钩子</span>
          <textarea
            data-testid={`episode-hook-editor-${index}`}
            onChange={(event) => onUpdateEpisodeField(index, "hook", event.target.value)}
            rows={3}
            value={episode.hook}
          />
        </label>
      ) : (
        episode.hook && <strong className="short-script-hook">钩子：{episode.hook}</strong>
      )}
      <div className="short-script-scene-list">{episode.scenes.map(renderScene)}</div>
    </article>
  );
}

export function ShortDramaEpisodeEditor({
  episodes,
  canEditFields = false,
  onUpdateEpisodeField,
}: ShortDramaEpisodeEditorProps) {
  if (episodes.length === 0) {
    return null;
  }

  return (
    <section className="short-script-section">
      <h3>分集内容</h3>
      <div className="short-script-episode-list">
        {episodes.map((episode, index) =>
          renderEpisode(episode, index, canEditFields, onUpdateEpisodeField),
        )}
      </div>
    </section>
  );
}
