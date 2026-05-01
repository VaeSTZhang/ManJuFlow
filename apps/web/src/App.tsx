import { FormEvent, useEffect, useState } from "react";
import { generateImagePrompts } from "./api/imagePrompts";
import { generateStoryboard } from "./api/storyboards";
import "./App.css";
import type { ImagePromptInput, ImagePromptOutput } from "./types/imagePrompt";
import type { StoryboardInput, StoryboardOutput } from "./types/storyboard";

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

type SystemStatus = {
  app_name: string;
  app_env: string;
  script_generation_mode: string;
  llm_enabled: boolean;
  status: string;
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

const defaultStoryboardForm: StoryboardInput = {
  project_title: "测试短剧：雨夜重逢",
  script_text:
    "第1集 第1场｜医院门口｜雨夜。暴雨中，林晚撑着黑伞站在医院门口，顾沉从车里下来，两人隔雨对视。顾沉：你终于肯回来了？林晚：我回来，不是为了见你。",
};

const defaultImagePromptForm: ImagePromptInput = {
  project_title: "测试短剧：雨夜重逢",
  storyboard_text:
    "第1场｜医院门口｜雨夜。镜头1：林晚撑着黑伞站在医院门口台阶边，雨水打湿地面。镜头2：顾沉从黑色轿车里下来，两人在车灯和雨幕中对视。",
  target_model: "general",
  aspect_ratio: "9:16",
  style_preset: "cinematic realistic",
  language: "en",
  extra_requirements: "保持雨夜、冷色光影、电影感写实风格。",
};

function formatScriptForStoryboard(script: ScriptOutput): string {
  const characters = script.characters
    .map(
      (character) =>
        `- ${character.name}（${character.role}）：${character.age}，${character.personality}。人物弧光：${character.arc}`,
    )
    .join("\n");

  const episodes = script.episodes
    .map((episode) => {
      const scenes = episode.scenes
        .map((scene) => {
          const dialogues = scene.dialogues
            .map((dialogue) => `    ${dialogue.character}：${dialogue.line}`)
            .join("\n");

          return [
            `  第 ${scene.scene_number} 场｜${scene.location}｜${scene.time}`,
            `  场景描述：${scene.description}`,
            `  画面说明：${scene.visual_notes}`,
            `  情绪曲线：${scene.emotion_curve}`,
            dialogues ? `  对白：\n${dialogues}` : "  对白：无",
          ].join("\n");
        })
        .join("\n\n");

      return [
        `第 ${episode.episode_number} 集：${episode.title}`,
        `概要：${episode.summary}`,
        `钩子：${episode.hook}`,
        scenes,
      ].join("\n");
    })
    .join("\n\n");

  return [
    `项目标题：${script.project_title}`,
    `故事梗概：${script.logline}`,
    `世界观设定：${script.world_setting}`,
    "主要人物：",
    characters || "无",
    "分集与场景：",
    episodes || "无",
  ].join("\n\n");
}

function formatStoryboardForImagePrompt(storyboard: StoryboardOutput): string {
  const scenes = storyboard.scenes
    .map((scene) => {
      const shots = scene.shots
        .map((shot) =>
          [
            `镜头 ${shot.shot_number}｜${shot.shot_id}`,
            `景别：${shot.shot_type}`,
            `机位：${shot.camera_angle}`,
            `运动：${shot.camera_movement}`,
            `画面：${shot.visual_description}`,
            `绘图提示：${shot.ai_image_prompt_hint || "无"}`,
          ].join("\n"),
        )
        .join("\n\n");

      return [
        `场景 ${scene.scene_number}｜${scene.scene_id}｜${scene.location}｜${scene.time}`,
        `摘要：${scene.scene_summary}`,
        `冲突：${scene.scene_conflict}`,
        shots,
      ].join("\n");
    })
    .join("\n\n");

  return [`项目标题：${storyboard.project_title}`, `分镜说明：${storyboard.storyboard_summary}`, scenes].join("\n\n");
}

function sanitizeFileName(value: string): string {
  return value
    .trim()
    .replace(/[\\/:*?"<>|]/g, "-")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60);
}

const stages = [
  {
    title: "灵感输入",
    description: "整理创意、题材、平台和风格要求，形成可生成的结构化输入。",
  },
  {
    title: "结构化剧本",
    description: "输出标题、卖点、世界观、角色、分集和场景对白。",
  },
  {
    title: "前端展示",
    description: "以工作台形式预览生成结果，便于内部评审和演示。",
  },
  {
    title: "复制 / 导出",
    description: "保留完整 JSON，方便后续进入 Prompt、模型和生产流程。",
  },
];

function App() {
  const [form, setForm] = useState<IdeaInput>(defaultForm);
  const [result, setResult] = useState<ScriptOutput | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isSystemConnected, setIsSystemConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [copyStatus, setCopyStatus] = useState("");
  const [exportStatus, setExportStatus] = useState("");
  const [storyboardForm, setStoryboardForm] = useState<StoryboardInput>(defaultStoryboardForm);
  const [storyboardResult, setStoryboardResult] = useState<StoryboardOutput | null>(null);
  const [isStoryboardLoading, setIsStoryboardLoading] = useState(false);
  const [storyboardError, setStoryboardError] = useState("");
  const [storyboardCopyStatus, setStoryboardCopyStatus] = useState("");
  const [storyboardExportStatus, setStoryboardExportStatus] = useState("");
  const [storyboardTransferStatus, setStoryboardTransferStatus] = useState("");
  const [imagePromptForm, setImagePromptForm] = useState<ImagePromptInput>(defaultImagePromptForm);
  const [imagePromptResult, setImagePromptResult] = useState<ImagePromptOutput | null>(null);
  const [imagePromptLoading, setImagePromptLoading] = useState(false);
  const [imagePromptError, setImagePromptError] = useState("");
  const [imagePromptTransferStatus, setImagePromptTransferStatus] = useState("");
  const [imagePromptCopyStatus, setImagePromptCopyStatus] = useState("");
  const [imagePromptExportStatus, setImagePromptExportStatus] = useState("");

  useEffect(() => {
    const loadSystemStatus = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/system/status");

        if (!response.ok) {
          throw new Error("状态接口请求失败");
        }

        const data = (await response.json()) as SystemStatus;
        setSystemStatus(data);
        setIsSystemConnected(true);
      } catch {
        setSystemStatus(null);
        setIsSystemConnected(false);
      }
    };

    loadSystemStatus();
  }, []);

  const updateField = <K extends keyof IdeaInput>(field: K, value: IdeaInput[K]) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const updateStoryboardField = <K extends keyof StoryboardInput>(field: K, value: StoryboardInput[K]) => {
    setStoryboardForm((current) => ({ ...current, [field]: value }));
    setStoryboardTransferStatus("");
  };

  const updateImagePromptField = <K extends keyof ImagePromptInput>(field: K, value: ImagePromptInput[K]) => {
    setImagePromptForm((current) => ({ ...current, [field]: value }));
    setImagePromptTransferStatus("");
    setImagePromptCopyStatus("");
    setImagePromptExportStatus("");
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    setCopyStatus("");
    setExportStatus("");
    setStoryboardTransferStatus("");

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
      setError("生成失败，请确认后端服务已启动：http://127.0.0.1:8000");
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
    setExportStatus("");
  };

  const exportJson = () => {
    if (!result) {
      return;
    }

    const json = JSON.stringify(result, null, 2);
    const blob = new Blob([json], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "manjuflow-script-output.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    setExportStatus("已导出");
    setCopyStatus("");
  };

  const transferScriptToStoryboard = () => {
    if (!result) {
      return;
    }

    setStoryboardForm((current) => ({
      ...current,
      project_title: result.project_title,
      script_text: formatScriptForStoryboard(result),
    }));
    setStoryboardTransferStatus("已带入分镜生成区域");
    setStoryboardError("");
    setStoryboardCopyStatus("");
    setStoryboardExportStatus("");
  };

  const transferStoryboardToImagePrompt = () => {
    if (!storyboardResult) {
      return;
    }

    setImagePromptForm((current) => ({
      ...current,
      project_title: storyboardResult.project_title,
      storyboard_summary: storyboardResult.storyboard_summary,
      storyboard_text: formatStoryboardForImagePrompt(storyboardResult),
    }));
    setImagePromptTransferStatus("已带入绘图 Prompt 生成区域");
    setImagePromptError("");
    setImagePromptCopyStatus("");
    setImagePromptExportStatus("");
  };

  const handleStoryboardSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsStoryboardLoading(true);
    setStoryboardError("");
    setStoryboardCopyStatus("");
    setStoryboardExportStatus("");
    setStoryboardTransferStatus("");

    try {
      const data = await generateStoryboard(storyboardForm);
      setStoryboardResult(data);
    } catch {
      setStoryboardError("生成分镜失败，请确认后端服务已启动：http://127.0.0.1:8000");
    } finally {
      setIsStoryboardLoading(false);
    }
  };

  const copyStoryboardJson = async () => {
    if (!storyboardResult) {
      return;
    }

    await navigator.clipboard.writeText(JSON.stringify(storyboardResult, null, 2));
    setStoryboardCopyStatus("已复制分镜 JSON");
    setStoryboardExportStatus("");
  };

  const exportStoryboardJson = () => {
    if (!storyboardResult) {
      return;
    }

    const json = JSON.stringify(storyboardResult, null, 2);
    const blob = new Blob([json], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "manjuflow-storyboard-output.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    setStoryboardExportStatus("已导出分镜 JSON");
    setStoryboardCopyStatus("");
  };

  const handleImagePromptSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!imagePromptForm.project_title.trim()) {
      setImagePromptError("请先填写项目标题。");
      return;
    }

    if (!imagePromptForm.storyboard_text?.trim()) {
      setImagePromptError("请先填写分镜文本。");
      return;
    }

    setImagePromptLoading(true);
    setImagePromptError("");
    setImagePromptTransferStatus("");
    setImagePromptCopyStatus("");
    setImagePromptExportStatus("");

    try {
      const data = await generateImagePrompts({
        ...imagePromptForm,
        project_title: imagePromptForm.project_title.trim(),
        storyboard_text: imagePromptForm.storyboard_text.trim(),
        target_model: imagePromptForm.target_model || "general",
        aspect_ratio: imagePromptForm.aspect_ratio || "9:16",
        style_preset: imagePromptForm.style_preset || "cinematic realistic",
        language: imagePromptForm.language || "en",
      });
      setImagePromptResult(data);
    } catch {
      setImagePromptError("生成绘图 Prompt 失败，请确认后端服务已启动：http://127.0.0.1:8000");
    } finally {
      setImagePromptLoading(false);
    }
  };

  const copyImagePromptJson = async () => {
    if (!imagePromptResult) {
      return;
    }

    try {
      await navigator.clipboard.writeText(JSON.stringify(imagePromptResult, null, 2));
      setImagePromptCopyStatus("已复制绘图 Prompt JSON");
      setImagePromptExportStatus("");
      setImagePromptError("");
    } catch {
      setImagePromptError("复制绘图 Prompt JSON 失败，请检查浏览器剪贴板权限。");
    }
  };

  const exportImagePromptJson = () => {
    if (!imagePromptResult) {
      return;
    }

    const json = JSON.stringify(imagePromptResult, null, 2);
    const blob = new Blob([json], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const safeTitle = sanitizeFileName(imagePromptResult.project_title) || "output";

    link.href = url;
    link.download = `image-prompts-${safeTitle}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    setImagePromptExportStatus("已导出绘图 Prompt JSON");
    setImagePromptCopyStatus("");
    setImagePromptError("");
  };

  return (
    <main className="app">
      <header className="page-header">
        <div>
          <p className="eyebrow">内部 AI 创作工作台</p>
          <h1>ManJuFlow｜漫剧流</h1>
          <p className="subtitle">AI 影视化创作流水线 · 第一阶段 MVP</p>
          <p className="description">
            从灵感输入到结构化短剧剧本输出，帮助 AI 生成部门快速获得可复用创作素材。
          </p>
        </div>

        <aside className="system-status" aria-label="后端系统状态">
          <div className={isSystemConnected ? "status-dot status-ok" : "status-dot status-offline"} />
          <div>
            <p>{isSystemConnected ? `后端状态：${systemStatus?.status}` : "后端状态：未连接"}</p>
            {isSystemConnected && systemStatus && (
              <>
                <p>运行环境：{systemStatus.app_env}</p>
                <p>生成模式：{systemStatus.script_generation_mode}</p>
                <p>LLM：{systemStatus.llm_enabled ? "已启用" : "未启用"}</p>
              </>
            )}
          </div>
        </aside>
      </header>

      <section className="stage-grid" aria-label="第一阶段 MVP 状态">
        {stages.map((stage, index) => (
          <article className="stage-card" key={stage.title}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <h2>{stage.title}</h2>
            <p>{stage.description}</p>
          </article>
        ))}
      </section>

      <section className="workspace">
        <form className="panel form-panel" onSubmit={handleSubmit}>
          <div className="panel-heading">
            <p>输入配置</p>
            <h2>创作灵感</h2>
          </div>

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
            <div>
              <p>输出预览</p>
              <h2>结构化剧本</h2>
            </div>
            <div className="result-actions">
              <button className="secondary-button" disabled={!result} onClick={transferScriptToStoryboard} type="button">
                带入分镜生成
              </button>
              <button className="secondary-button" disabled={!result} onClick={copyJson} type="button">
                复制 JSON
              </button>
              <button className="secondary-button" disabled={!result} onClick={exportJson} type="button">
                导出 JSON
              </button>
            </div>
          </div>

          {copyStatus && <p className="copy-status">{copyStatus}</p>}
          {exportStatus && <p className="copy-status">{exportStatus}</p>}
          {storyboardTransferStatus && <p className="copy-status">{storyboardTransferStatus}</p>}

          {!result ? (
            <div className="empty-state">输入灵感后，生成结果将在这里展示。</div>
          ) : (
            <article className="script-output">
              <section className="result-summary">
                <span>项目标题</span>
                <h3>{result.project_title}</h3>
              </section>

              <section className="info-block">
                <h4>一句话卖点</h4>
                <p>{result.logline}</p>
              </section>

              <section className="info-block">
                <h4>世界观设定</h4>
                <p>{result.world_setting}</p>
              </section>

              <section className="content-section">
                <h4>角色列表</h4>
                <div className="item-list character-list">
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
              </section>

              <section className="content-section">
                <h4>分集大纲</h4>
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
                          场景内容 {scene.scene_number} · {scene.location} · {scene.time}
                        </h6>
                        <p>{scene.description}</p>
                        <p>画面说明：{scene.visual_notes}</p>
                        <p>情绪曲线：{scene.emotion_curve}</p>
                        <p className="dialogue-title">对白</p>
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
              </section>
            </article>
          )}
        </section>
      </section>

      <section className="storyboard-workspace">
        <form className="panel form-panel" onSubmit={handleStoryboardSubmit}>
          <div className="panel-heading">
            <p>第二阶段</p>
            <h2>生成分镜</h2>
          </div>

          <label className="field field-wide">
            <span>项目标题</span>
            <input
              value={storyboardForm.project_title}
              onChange={(event) => updateStoryboardField("project_title", event.target.value)}
            />
          </label>

          <label className="field field-wide">
            <span>剧本文本</span>
            <textarea
              value={storyboardForm.script_text}
              onChange={(event) => updateStoryboardField("script_text", event.target.value)}
              rows={7}
            />
          </label>

          <button className="primary-button" disabled={isStoryboardLoading} type="submit">
            {isStoryboardLoading ? "生成中..." : "生成分镜"}
          </button>

          {storyboardError && <p className="error-message">{storyboardError}</p>}
        </form>

        <section className="panel result-panel">
          <div className="result-header">
            <div>
              <p>输出预览</p>
              <h2>分镜结果</h2>
            </div>
            <div className="result-actions">
              <button
                className="secondary-button"
                disabled={!storyboardResult}
                onClick={transferStoryboardToImagePrompt}
                type="button"
              >
                带入绘图 Prompt
              </button>
              <button className="secondary-button" disabled={!storyboardResult} onClick={copyStoryboardJson} type="button">
                复制分镜 JSON
              </button>
              <button className="secondary-button" disabled={!storyboardResult} onClick={exportStoryboardJson} type="button">
                导出分镜 JSON
              </button>
            </div>
          </div>

          {storyboardCopyStatus && <p className="copy-status">{storyboardCopyStatus}</p>}
          {storyboardExportStatus && <p className="copy-status">{storyboardExportStatus}</p>}
          {imagePromptTransferStatus && <p className="copy-status">{imagePromptTransferStatus}</p>}

          {!storyboardResult ? (
            <div className="empty-state">输入剧本文本后，分镜结果将在这里展示。</div>
          ) : (
            <article className="script-output storyboard-output">
              <section className="result-summary">
                <span>项目标题</span>
                <h3>{storyboardResult.project_title}</h3>
                <p>第 {storyboardResult.episode_number} 集</p>
              </section>

              <section className="storyboard-summary-block">
                <h4>分镜说明</h4>
                <p>{storyboardResult.storyboard_summary}</p>
              </section>

              <section className="storyboard-scenes">
                <h4>场景分镜</h4>
                <div className="storyboard-scene-list">
                  {storyboardResult.scenes.map((scene) => (
                    <section className="storyboard-scene-card" key={scene.scene_number}>
                      <div className="storyboard-scene-header">
                        <span>{scene.scene_id}</span>
                        <h5>
                          场景 {scene.scene_number} · {scene.location} · {scene.time}
                        </h5>
                      </div>

                      <div className="storyboard-scene-meta">
                        <p>
                          <strong>摘要</strong>
                          {scene.scene_summary}
                        </p>
                        <p>
                          <strong>冲突</strong>
                          {scene.scene_conflict}
                        </p>
                      </div>

                      <div className="shot-list">
                        {scene.shots.map((shot) => (
                          <section className="storyboard-shot-card" key={`${scene.scene_number}-${shot.shot_number}`}>
                            <div className="shot-title-row">
                              <span>{shot.shot_id}</span>
                              <h6>{shot.shot_type}</h6>
                            </div>

                            <dl className="shot-detail-grid">
                              <div>
                                <dt>机位角度</dt>
                                <dd>{shot.camera_angle}</dd>
                              </div>
                              <div>
                                <dt>镜头运动</dt>
                                <dd>{shot.camera_movement}</dd>
                              </div>
                              <div>
                                <dt>画面主体</dt>
                                <dd>{shot.subject}</dd>
                              </div>
                              <div>
                                <dt>人物动作</dt>
                                <dd>{shot.action}</dd>
                              </div>
                              <div>
                                <dt>情绪重点</dt>
                                <dd>{shot.emotion}</dd>
                              </div>
                              <div>
                                <dt>建议时长</dt>
                                <dd>{shot.duration_seconds ?? "未设置"} 秒</dd>
                              </div>
                            </dl>

                            <div className="visual-description">
                              <span>完整画面描述</span>
                              <p>{shot.visual_description}</p>
                            </div>

                            <div className="prompt-hint">
                              <span>AI 绘图提示</span>
                              <p>{shot.ai_image_prompt_hint || "无"}</p>
                            </div>
                          </section>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              </section>
            </article>
          )}
        </section>
      </section>

      <section className="image-prompt-workspace">
        <form className="panel form-panel" onSubmit={handleImagePromptSubmit}>
          <div className="panel-heading">
            <p>第三阶段</p>
            <h2>生成绘图 Prompt</h2>
          </div>

          <label className="field field-wide">
            <span>项目标题</span>
            <input
              value={imagePromptForm.project_title}
              onChange={(event) => updateImagePromptField("project_title", event.target.value)}
            />
          </label>

          <label className="field field-wide">
            <span>分镜文本</span>
            <textarea
              value={imagePromptForm.storyboard_text || ""}
              onChange={(event) => updateImagePromptField("storyboard_text", event.target.value)}
              rows={8}
            />
          </label>

          <div className="field-grid">
            <label className="field">
              <span>目标模型</span>
              <input
                value={imagePromptForm.target_model || "general"}
                onChange={(event) => updateImagePromptField("target_model", event.target.value)}
              />
            </label>

            <label className="field">
              <span>画面比例</span>
              <select
                value={imagePromptForm.aspect_ratio || "9:16"}
                onChange={(event) => updateImagePromptField("aspect_ratio", event.target.value)}
              >
                <option value="9:16">9:16</option>
                <option value="16:9">16:9</option>
                <option value="1:1">1:1</option>
                <option value="4:5">4:5</option>
              </select>
            </label>

            <label className="field">
              <span>风格预设</span>
              <input
                value={imagePromptForm.style_preset || "cinematic realistic"}
                onChange={(event) => updateImagePromptField("style_preset", event.target.value)}
              />
            </label>

            <label className="field">
              <span>语言</span>
              <select
                value={imagePromptForm.language || "en"}
                onChange={(event) => updateImagePromptField("language", event.target.value)}
              >
                <option value="en">en</option>
                <option value="zh">zh</option>
              </select>
            </label>
          </div>

          <label className="field field-wide">
            <span>额外要求</span>
            <textarea
              value={imagePromptForm.extra_requirements || ""}
              onChange={(event) => updateImagePromptField("extra_requirements", event.target.value)}
              rows={3}
            />
          </label>

          <button className="primary-button" disabled={imagePromptLoading} type="submit">
            {imagePromptLoading ? "生成中..." : "生成绘图 Prompt"}
          </button>

          {imagePromptError && <p className="error-message">{imagePromptError}</p>}
        </form>

        <section className="panel result-panel">
          <div className="result-header">
            <div>
              <p>输出预览</p>
              <h2>绘图 Prompt</h2>
            </div>
            <div className="result-actions">
              <button
                className="secondary-button"
                disabled={!imagePromptResult}
                onClick={copyImagePromptJson}
                type="button"
              >
                复制绘图 Prompt JSON
              </button>
              <button
                className="secondary-button"
                disabled={!imagePromptResult}
                onClick={exportImagePromptJson}
                type="button"
              >
                导出绘图 Prompt JSON
              </button>
            </div>
          </div>

          {imagePromptCopyStatus && <p className="copy-status">{imagePromptCopyStatus}</p>}
          {imagePromptExportStatus && <p className="copy-status">{imagePromptExportStatus}</p>}

          {!imagePromptResult ? (
            <div className="empty-state">输入分镜文本后，绘图 Prompt 结果将在这里展示。</div>
          ) : (
            <article className="script-output image-prompt-output">
              <section className="result-summary">
                <span>项目标题</span>
                <h3>{imagePromptResult.project_title}</h3>
                <p>{imagePromptResult.prompt_summary}</p>
              </section>

              <section className="image-prompt-meta">
                <div>
                  <span>目标模型</span>
                  <strong>{imagePromptResult.target_model}</strong>
                </div>
                <div>
                  <span>画面比例</span>
                  <strong>{imagePromptResult.aspect_ratio}</strong>
                </div>
                <div>
                  <span>风格预设</span>
                  <strong>{imagePromptResult.style_preset}</strong>
                </div>
                <div>
                  <span>条目数量</span>
                  <strong>{imagePromptResult.items.length}</strong>
                </div>
              </section>

              <section className="image-prompt-items">
                <h4>Prompt 条目</h4>
                <div className="image-prompt-list">
                  {imagePromptResult.items.map((item) => (
                    <section className="image-prompt-card" key={item.prompt_id}>
                      <div className="prompt-card-header">
                        <span>{item.prompt_id}</span>
                        <h5>{item.shot_id}</h5>
                      </div>

                      <div className="prompt-text-block positive-prompt">
                        <span>Positive Prompt</span>
                        <p>{item.positive_prompt}</p>
                      </div>

                      <div className="prompt-text-block negative-prompt">
                        <span>Negative Prompt</span>
                        <p>{item.negative_prompt}</p>
                      </div>

                      <dl className="prompt-detail-grid">
                        <div>
                          <dt>镜头语言</dt>
                          <dd>{item.camera_language || "未设置"}</dd>
                        </div>
                        <div>
                          <dt>光影</dt>
                          <dd>{item.lighting || "未设置"}</dd>
                        </div>
                        <div>
                          <dt>构图</dt>
                          <dd>{item.composition || "未设置"}</dd>
                        </div>
                        <div>
                          <dt>模型提示</dt>
                          <dd>{item.model_hint || "未设置"}</dd>
                        </div>
                      </dl>
                    </section>
                  ))}
                </div>
              </section>
            </article>
          )}
        </section>
      </section>
    </main>
  );
}

export default App;
