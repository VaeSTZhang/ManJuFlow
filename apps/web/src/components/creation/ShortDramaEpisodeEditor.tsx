import type { DialogueLine, EpisodeScript, SceneScript } from "../../types/scriptGeneration";

type ShortDramaEpisodeEditorProps = {
  episodes: EpisodeScript[];
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

export function ShortDramaEpisodeEditor({ episodes }: ShortDramaEpisodeEditorProps) {
  if (episodes.length === 0) {
    return null;
  }

  return (
    <section className="short-script-section">
      <h3>分集内容</h3>
      <div className="short-script-episode-list">{episodes.map(renderEpisode)}</div>
    </section>
  );
}
