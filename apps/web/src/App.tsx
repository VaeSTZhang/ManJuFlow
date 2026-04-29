import { FormEvent, useState } from "react";
import "./App.css";

type IdeaInput = {
  idea_text: string;
  script_type: string;
  genre: string;
  episode_count: number;
  episode_duration: string;
  target_platform: string;
  tone: string;
  audience: string;
  style_requirements: string;
};

type CharacterProfile = {
  name: string;
  role: string;
  age: string;
  personality: string;
  arc: string;
};

type DialogueLine = {
  character: string;
  line: string;
};

type SceneScript = {
  scene_number: number;
  location: string;
  time: string;
  description: string;
  dialogues: DialogueLine[];
  visual_notes: string;
  emotion_curve: string;
};

type EpisodeScript = {
  episode_number: number;
  title: string;
  summary: string;
  hook: string;
  scenes: SceneScript[];
};

type ScriptOutput = {
  project_title: string;
  logline: string;
  world_setting: string;
  characters: CharacterProfile[];
  episodes: EpisodeScript[];
};

const defaultForm: IdeaInput = {
  idea_text: "一个被裁员的中年男人，意外发现公司老板用AI伪造财报",
  script_type: "短剧",
  genre: "都市悬疑",
  episode_count: 1,
  episode_duration: "3-5分钟",
  target_platform: "短视频平台",
  tone: "节奏快、钩子强、反转明显",
  audience: "短剧观众",
  style_requirements: "开头要有强冲突，结尾要有反转",
};

function App() {
  const [form, setForm] = useState<IdeaInput>(defaultForm);
  const [result, setResult] = useState<ScriptOutput | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [copyStatus, setCopyStatus] = useState("");

  const updateField = <K extends keyof IdeaInput>(field: K, value: IdeaInput[K]) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    setCopyStatus("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/scripts/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw new Error("请求失败");
      }

      const data = (await response.json()) as ScriptOutput;
      setResult(data);
    } catch {
      setError("请确认后端服务已启动");
    } finally {
      setIsLoading(false);
    }
  };

  const copyJson = async () => {
    if (!result) {
      return;
    }

    await navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopyStatus("已复制");
  };

  return (
    <main className="app">
      <header className="page-header">
        <h1>ManJuFlow｜漫剧流</h1>
        <p>AI 影视化创作流水线 · 第一阶段 MVP</p>
      </header>

      <section className="workspace">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <label className="field field-wide">
            <span>灵感输入</span>
            <textarea
              value={form.idea_text}
              onChange={(event) => updateField("idea_text", event.target.value)}
              rows={5}
            />
          </label>

          <div className="field-grid">
            <label className="field">
              <span>剧本类型</span>
              <input
                value={form.script_type}
                onChange={(event) => updateField("script_type", event.target.value)}
              />
            </label>

            <label className="field">
              <span>类型风格</span>
              <input value={form.genre} onChange={(event) => updateField("genre", event.target.value)} />
            </label>

            <label className="field">
              <span>集数</span>
              <input
                min={1}
                type="number"
                value={form.episode_count}
                onChange={(event) => updateField("episode_count", Number(event.target.value) || 1)}
              />
            </label>

            <label className="field">
              <span>单集时长</span>
              <input
                value={form.episode_duration}
                onChange={(event) => updateField("episode_duration", event.target.value)}
              />
            </label>

            <label className="field">
              <span>目标平台</span>
              <input
                value={form.target_platform}
                onChange={(event) => updateField("target_platform", event.target.value)}
              />
            </label>

            <label className="field">
              <span>目标受众</span>
              <input value={form.audience} onChange={(event) => updateField("audience", event.target.value)} />
            </label>
          </div>

          <label className="field field-wide">
            <span>风格语气</span>
            <input value={form.tone} onChange={(event) => updateField("tone", event.target.value)} />
          </label>

          <label className="field field-wide">
            <span>额外要求</span>
            <input
              value={form.style_requirements}
              onChange={(event) => updateField("style_requirements", event.target.value)}
            />
          </label>

          <button className="primary-button" disabled={isLoading} type="submit">
            {isLoading ? "生成中..." : "生成结构化剧本"}
          </button>

          {error && <p className="error-message">{error}</p>}
        </form>

        <section className="panel result-panel">
          <div className="result-header">
            <h2>生成结果</h2>
            <button className="secondary-button" disabled={!result} onClick={copyJson} type="button">
              复制 JSON
            </button>
          </div>

          {copyStatus && <p className="copy-status">{copyStatus}</p>}

          {!result ? (
            <p className="empty-state">提交灵感后，这里会展示结构化剧本结果。</p>
          ) : (
            <article className="script-output">
              <h3>{result.project_title}</h3>
              <p>
                <strong>一句话卖点：</strong>
                {result.logline}
              </p>
              <p>
                <strong>世界观设定：</strong>
                {result.world_setting}
              </p>

              <h4>角色列表</h4>
              <div className="item-list">
                {result.characters.map((character) => (
                  <section className="item" key={character.name}>
                    <h5>
                      {character.name} · {character.role}
                    </h5>
                    <p>年龄：{character.age}</p>
                    <p>性格：{character.personality}</p>
                    <p>人物弧光：{character.arc}</p>
                  </section>
                ))}
              </div>

              <h4>分集内容</h4>
              <div className="item-list">
                {result.episodes.map((episode) => (
                  <section className="item" key={episode.episode_number}>
                    <h5>
                      第 {episode.episode_number} 集：{episode.title}
                    </h5>
                    <p>概要：{episode.summary}</p>
                    <p>钩子：{episode.hook}</p>

                    {episode.scenes.map((scene) => (
                      <section className="scene" key={scene.scene_number}>
                        <h6>
                          场景 {scene.scene_number} · {scene.location} · {scene.time}
                        </h6>
                        <p>{scene.description}</p>
                        <p>画面说明：{scene.visual_notes}</p>
                        <p>情绪曲线：{scene.emotion_curve}</p>
                        <ul>
                          {scene.dialogues.map((dialogue, index) => (
                            <li key={`${dialogue.character}-${index}`}>
                              <strong>{dialogue.character}：</strong>
                              {dialogue.line}
                            </li>
                          ))}
                        </ul>
                      </section>
                    ))}
                  </section>
                ))}
              </div>
            </article>
          )}
        </section>
      </section>
    </main>
  );
}

export default App;
