import { useState } from "react";
import {
  CreativeModelPanel,
  type SelectedCreativeModel,
} from "../ai/CreativeModelPanel";
import { ShortDramaScriptResult } from "./ShortDramaScriptResult";
import type {
  AdaptationNotes,
  DialogueLine,
  EpisodeScript,
  SceneScript,
  ScriptSourceMode,
  ShortDramaScriptOutput,
} from "../../types/scriptGeneration";

type CreationMode = "idea" | "adaptation";
type AdaptationMode = "film" | "novel";

type IdeaCreationDraft = {
  projectTitle: string;
  ideaText: string;
  genreStyle: string;
  episodeCount: number;
  extraRequirements: string;
};

type AdaptationDraft = {
  projectTitle: string;
  sourceTitle: string;
  sourceText: string;
  focus: string;
  episodeCount: number;
  extraRequirements: string;
};

type CreationDrafts = {
  idea: IdeaCreationDraft;
  film: AdaptationDraft;
  novel: AdaptationDraft;
};

type CreationHomeProps = {
  isAuthenticated: boolean;
  onRequireLogin: () => void;
};

type MockGenerationDraft = {
  projectTitle: string;
  sourceMode: Extract<ScriptSourceMode, "idea" | "film_script" | "novel">;
  sourceLabel: string;
  premise: string;
  genreStyle: string;
  episodeCount: number;
  focus?: string;
  sourceTitle?: string;
  extraRequirements?: string;
};

const defaultCreationDrafts: CreationDrafts = {
  idea: {
    projectTitle: "",
    ideaText: "",
    genreStyle: "悬疑短剧 / 强钩子、快节奏",
    episodeCount: 10,
    extraRequirements: "",
  },
  film: {
    projectTitle: "",
    sourceTitle: "",
    sourceText: "",
    focus: "",
    episodeCount: 10,
    extraRequirements: "",
  },
  novel: {
    projectTitle: "",
    sourceTitle: "",
    sourceText: "",
    focus: "",
    episodeCount: 10,
    extraRequirements: "",
  },
};

const defaultCreativeModel: SelectedCreativeModel = {
  provider: "deepseek",
  model: "deepseek-chat",
  label: "DeepSeek",
  source: "user_selected",
};

function normalizeText(value: string | undefined, fallback: string): string {
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : fallback;
}

function clampEpisodeCount(value: number): number {
  if (!Number.isFinite(value)) {
    return 1;
  }

  return Math.min(Math.max(Math.round(value), 1), 24);
}

function buildModelLabel(selectedModel: SelectedCreativeModel): string {
  return selectedModel.model ? `${selectedModel.label} / ${selectedModel.model}` : selectedModel.label;
}

function buildScene(
  sceneNumber: number,
  location: string,
  time: string,
  description: string,
  dialogues: DialogueLine[],
  visualNotes: string,
  emotionCurve: string,
): SceneScript {
  return {
    scene_number: sceneNumber,
    location,
    time,
    description,
    dialogues,
    visual_notes: visualNotes,
    emotion_curve: emotionCurve,
  };
}

function buildEpisode(index: number, projectTitle: string, premise: string, focus: string): EpisodeScript {
  const isOpening = index === 1;

  return {
    episode_number: index,
    title: isOpening ? "钩子开场" : `第 ${index} 次反转`,
    summary: isOpening
      ? `${projectTitle} 以强冲突开场，主角被迫面对 ${premise} 带来的第一道选择。`
      : `围绕 ${focus} 推进人物关系，旧线索被重新解释，结尾留下新的选择压力。`,
    hook: isOpening
      ? "主角在最不该暴露真相的时刻，被迫公开一个关键秘密。"
      : "上一场看似解决的问题，在结尾变成更大的误会和危机。",
    scenes: [
      buildScene(
        1,
        isOpening ? "公司走廊" : "临时会议室",
        isOpening ? "清晨" : "夜晚",
        isOpening
          ? "主角在拥挤走廊里听见一段关键对话，意识到自己被卷入一场精心安排的局。"
          : "主角和搭档复盘线索，发现真正被隐瞒的不是事件本身，而是背后的动机。",
        [
          { character: "林夏", line: "如果现在退后，我们就只剩下被安排的结局。" },
          { character: "顾然", line: "那就别退。先把最危险的那一页翻开。" },
        ],
        "镜头贴近人物表情，环境保持克制，让信息和情绪成为重点。",
        isOpening ? "压迫感快速升高" : "怀疑转为短暂同盟",
      ),
      buildScene(
        2,
        isOpening ? "天台" : "旧档案室",
        isOpening ? "傍晚" : "深夜",
        isOpening
          ? "主角独自整理线索，却收到一条来自陌生人的提醒，结尾出现第一处反转。"
          : "两人找到旧证据，但证据指向的对象与预期完全相反。",
        [
          { character: "林夏", line: "你早就知道这件事，对不对？" },
          { character: "顾然", line: "我知道的不够多，但足够证明我们都被骗了。" },
        ],
        "场景用少量道具承载线索，结尾给出清晰视觉记忆点。",
        isOpening ? "孤立无援转为主动追查" : "信任建立后立刻被新证据冲击",
      ),
    ],
  };
}

function buildAdaptationNotes(
  sourceMode: Extract<ScriptSourceMode, "film_script" | "novel">,
  sourceTitle: string,
  focus: string,
  extraRequirements: string,
): AdaptationNotes {
  const sourceType = sourceMode === "film_script" ? "原剧本" : "原小说 / 网文";

  return {
    source_mode: sourceMode,
    adaptation_strategy: `保留${sourceType}《${sourceTitle}》中的核心人物关系和主要冲突，将铺垫压缩为短剧节奏，并把 ${focus} 放到每集关键选择里。`,
    preserved_elements: ["核心人物关系", "主要矛盾", "关键情绪转折"],
    changed_elements: ["压缩长铺垫", "强化每集开场冲突", "把解释性段落改为可表演场景"],
    short_drama_hooks: ["开场 30 秒给出明确冲突", "每集结尾保留一次选择或反转", "对白服务人物关系推进"],
    risk_notes: [extraRequirements || "真实改编前需要确认素材授权与人工审阅。"],
  };
}

function generateMockShortDramaScript(draft: MockGenerationDraft): ShortDramaScriptOutput {
  const episodeCount = clampEpisodeCount(draft.episodeCount);
  const projectTitle = normalizeText(draft.projectTitle, "未命名短剧项目");
  const premise = normalizeText(draft.premise, "一个普通人在关键选择中发现身边关系并不简单");
  const focus = normalizeText(draft.focus, "人物关系、误会反转和每集结尾钩子");
  const genreStyle = normalizeText(draft.genreStyle, "都市情感 / 快节奏");
  const sourceTitle = normalizeText(draft.sourceTitle, projectTitle);
  const extraRequirements = normalizeText(draft.extraRequirements, "节奏紧凑，保留强钩子。");
  const episodes = Array.from({ length: episodeCount }, (_, index) =>
    buildEpisode(index + 1, projectTitle, premise, focus),
  );

  return {
    project_title: projectTitle,
    source_mode: draft.sourceMode,
    logline:
      draft.sourceMode === "idea"
        ? `围绕“${premise}”，主角在 ${genreStyle} 的短剧节奏中不断被迫选择，最终揭开真正的关系真相。`
        : `改编自“${sourceTitle}”的核心设定，围绕 ${focus} 形成适合短剧传播的强冲突连续剧本。`,
    world_setting: `故事发生在当代城市环境，人物关系紧密，信息差和情绪选择推动每集反转。创作要求：${extraRequirements}`,
    characters: [
      {
        name: "林夏",
        role: "女主 / 事件推动者",
        age: "28",
        personality: "敏锐、克制，不轻易相信表面解释。",
        arc: "从被动承受误解，到主动拆解关系真相。",
      },
      {
        name: "顾然",
        role: "男主 / 关键同盟",
        age: "31",
        personality: "冷静、有边界感，习惯用事实保护情绪。",
        arc: "从隐藏信息到选择共同承担风险。",
      },
    ],
    adaptation_notes:
      draft.sourceMode === "idea"
        ? null
        : buildAdaptationNotes(draft.sourceMode, sourceTitle, focus, extraRequirements),
    episode_count: episodeCount,
    episodes,
    metadata: {
      demo_mode: "local_frontend",
      source_label: draft.sourceLabel,
      generated_by: "CreationHome",
    },
  };
}

function downloadTextFile(filename: string, content: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function formatShortDramaScriptTxt(
  result: ShortDramaScriptOutput,
  sourceLabel: string,
  modelLabel: string,
  generatedAt: string,
): string {
  const characters = result.characters
    .map((character) => `- ${character.name}（${character.role}）：${character.personality} 人物弧光：${character.arc}`)
    .join("\n");

  const episodes = result.episodes
    .map((episode) => {
      const scenes = episode.scenes
        .map((scene) => {
          const dialogues = scene.dialogues
            .map((dialogue) => `    ${dialogue.character}：${dialogue.line}`)
            .join("\n");

          return [
            `  第 ${scene.scene_number} 场｜${scene.location}｜${scene.time}`,
            `  场景：${scene.description}`,
            dialogues ? `  对白：\n${dialogues}` : "  对白：无",
            `  画面：${scene.visual_notes}`,
            `  情绪：${scene.emotion_curve}`,
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

  const adaptation = result.adaptation_notes
    ? [
        "改编策略：",
        result.adaptation_notes.adaptation_strategy ?? "无",
        "保留元素：",
        result.adaptation_notes.preserved_elements.map((item) => `- ${item}`).join("\n"),
        "短剧钩子 / 爆点：",
        result.adaptation_notes.short_drama_hooks.map((item) => `- ${item}`).join("\n"),
      ].join("\n")
    : "改编策略：无";

  return [
    `项目标题：${result.project_title}`,
    `来源入口：${sourceLabel}`,
    `使用模型：${modelLabel}`,
    `生成时间：${generatedAt}`,
    "",
    `故事梗概：${result.logline}`,
    `世界观 / 故事背景：${result.world_setting}`,
    "",
    "主要人物：",
    characters || "无",
    "",
    adaptation,
    "",
    "分集内容：",
    episodes || "无",
  ].join("\n");
}

export function CreationHome({ isAuthenticated, onRequireLogin }: CreationHomeProps) {
  const [selectedMode, setSelectedMode] = useState<CreationMode | null>(null);
  const [selectedAdaptationMode, setSelectedAdaptationMode] = useState<AdaptationMode | null>(null);
  const [drafts, setDrafts] = useState<CreationDrafts>(defaultCreationDrafts);
  const [documentActionNotice, setDocumentActionNotice] = useState("");
  const [selectedCreativeModel, setSelectedCreativeModel] =
    useState<SelectedCreativeModel>(defaultCreativeModel);
  const [shortDramaResult, setShortDramaResult] = useState<ShortDramaScriptOutput | null>(null);
  const [shortDramaSourceLabel, setShortDramaSourceLabel] = useState<string | undefined>();
  const [shortDramaGeneratedAt, setShortDramaGeneratedAt] = useState<string | undefined>();

  const handlePrimarySelect = (mode: CreationMode) => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    setSelectedMode(mode);
    setDocumentActionNotice("");
    if (mode === "idea") {
      setSelectedAdaptationMode(null);
    }
  };

  const handleAdaptationSelect = (mode: AdaptationMode) => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    setSelectedMode("adaptation");
    setSelectedAdaptationMode(mode);
    setDocumentActionNotice("");
  };

  const handlePendingWordUpload = () => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    setDocumentActionNotice("真实 Word 上传将在文档导入闭环接入，当前可先粘贴文本。");
  };

  const updateIdeaDraft = <K extends keyof IdeaCreationDraft>(
    field: K,
    value: IdeaCreationDraft[K],
  ) => {
    setDrafts((current) => ({
      ...current,
      idea: {
        ...current.idea,
        [field]: value,
      },
    }));
  };

  const updateAdaptationDraft = <K extends keyof AdaptationDraft>(
    mode: AdaptationMode,
    field: K,
    value: AdaptationDraft[K],
  ) => {
    setDrafts((current) => ({
      ...current,
      [mode]: {
        ...current[mode],
        [field]: value,
      },
    }));
  };

  const resetSelection = () => {
    setSelectedMode(null);
    setSelectedAdaptationMode(null);
    setDocumentActionNotice("");
  };

  const setGeneratedResult = (result: ShortDramaScriptOutput, sourceLabel: string) => {
    setShortDramaResult(result);
    setShortDramaSourceLabel(sourceLabel);
    setShortDramaGeneratedAt(new Date().toLocaleString("zh-CN"));
  };

  const handleGenerateIdea = () => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    const draft = drafts.idea;
    const sourceLabel = "灵感生成";

    setGeneratedResult(
      generateMockShortDramaScript({
        projectTitle: draft.projectTitle,
        sourceMode: "idea",
        sourceLabel,
        premise: draft.ideaText,
        genreStyle: draft.genreStyle,
        episodeCount: draft.episodeCount,
        focus: "原创设定、人物关系和每集强钩子",
        extraRequirements: draft.extraRequirements,
      }),
      sourceLabel,
    );
  };

  const handleGenerateAdaptation = (mode: AdaptationMode) => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    const draft = drafts[mode];
    const isFilm = mode === "film";
    const sourceLabel = isFilm ? "电影剧本改编" : "小说 / 网文改编";

    setGeneratedResult(
      generateMockShortDramaScript({
        projectTitle: draft.projectTitle,
        sourceMode: isFilm ? "film_script" : "novel",
        sourceLabel,
        premise: draft.sourceText,
        genreStyle: isFilm ? "影视文本短剧化" : "小说 / 网文短剧化",
        episodeCount: draft.episodeCount,
        focus: draft.focus,
        sourceTitle: draft.sourceTitle,
        extraRequirements: draft.extraRequirements,
      }),
      sourceLabel,
    );
  };

  const handleCopyShortDramaJson = async () => {
    if (!shortDramaResult) {
      return;
    }

    await navigator.clipboard.writeText(JSON.stringify(shortDramaResult, null, 2));
  };

  const handleDownloadShortDramaJson = () => {
    if (!shortDramaResult) {
      return;
    }

    downloadTextFile(
      "dramora-short-drama-script.json",
      JSON.stringify(shortDramaResult, null, 2),
      "application/json;charset=utf-8",
    );
  };

  const handleDownloadShortDramaTxt = () => {
    if (!shortDramaResult) {
      return;
    }

    downloadTextFile(
      "dramora-short-drama-script.txt",
      formatShortDramaScriptTxt(
        shortDramaResult,
        shortDramaSourceLabel ?? "后端默认",
        buildModelLabel(selectedCreativeModel),
        shortDramaGeneratedAt ?? "生成后显示",
      ),
      "text/plain;charset=utf-8",
    );
  };

  const renderPrimaryCards = () => (
    <section className="creation-entry-section" aria-label="选择剧本创作方式">
      <div className="creation-entry-section-header">
        <span>剧本创作</span>
        <h2>选择剧本创作方式</h2>
        <p>先选择本次创作来源，再进入对应草稿区。当前页面不会自动调用生成接口。</p>
      </div>

      <div className="creation-entry-grid creation-entry-grid-two">
        <button
          className={`creation-entry-card${!isAuthenticated ? " locked" : ""}`}
          onClick={() => handlePrimarySelect("idea")}
          type="button"
        >
          <div className="creation-entry-card-header">
            <span>从一句创意开始</span>
            <h3>灵感生成短剧剧本</h3>
          </div>
          <p>输入故事灵感、人物关系或爽点方向，生成结构化短剧剧本。</p>
          <small>适合原创选题、短剧策划、故事方向验证。</small>
          <span className="creation-entry-card-action">开始生成</span>
        </button>

        <button
          className={`creation-entry-card${!isAuthenticated ? " locked" : ""}`}
          onClick={() => handlePrimarySelect("adaptation")}
          type="button"
        >
          <div className="creation-entry-card-header">
            <span>长文本短剧化</span>
            <h3>文本改编短剧本</h3>
          </div>
          <p>将电影剧本、小说、网文或长文本改编成短剧节奏。</p>
          <small>适合已有文本再开发、短剧化改编、内容二次整理。</small>
          <span className="creation-entry-card-action">开始改编</span>
        </button>
      </div>

      {!isAuthenticated && <p className="login-required-hint">请先登录后开始创作。</p>}
    </section>
  );

  const renderAdaptationChoices = () => (
    <section className="creation-draft-panel" aria-label="选择改编来源">
      <div className="creation-draft-header">
        <div className="panel-heading">
          <p>当前功能</p>
          <h2>文本改编短剧本</h2>
        </div>
        <button className="secondary-button" onClick={resetSelection} type="button">
          返回创作方式选择
        </button>
      </div>

      <p className="creation-draft-hint">
        选择文本来源后填写草稿。电影剧本和小说 / 网文会使用不同的改编思路，草稿会分别保留。
      </p>

      <div className="creation-entry-grid creation-entry-grid-two">
        <button
          className="creation-entry-card"
          onClick={() => handleAdaptationSelect("film")}
          type="button"
        >
          <div className="creation-entry-card-header">
            <span>影视文本改编</span>
            <h3>电影剧本改编</h3>
          </div>
          <p>将电影剧本、长剧本或分场文本改编成短剧节奏。</p>
          <span className="creation-entry-card-action">选择电影剧本改编</span>
        </button>

        <button
          className="creation-entry-card"
          onClick={() => handleAdaptationSelect("novel")}
          type="button"
        >
          <div className="creation-entry-card-header">
            <span>叙事文本改编</span>
            <h3>小说 / 网文改编</h3>
          </div>
          <p>将小说、网文或故事文本改编成可拍、可演、可分镜的短剧剧本。</p>
          <span className="creation-entry-card-action">选择小说 / 网文改编</span>
        </button>
      </div>
    </section>
  );

  const renderIdeaForm = () => {
    const draft = drafts.idea;

    return (
      <section className="creation-draft-panel" aria-label="灵感生成短剧草稿">
        <div className="creation-draft-header">
          <div className="panel-heading">
            <p>当前功能</p>
            <h2>灵感生成短剧剧本</h2>
          </div>
          <button className="secondary-button" onClick={resetSelection} type="button">
            返回创作方式选择
          </button>
        </div>

        <div className="creation-draft-form">
          <div className="creation-draft-grid">
            <label className="field creation-draft-field">
              <span>项目标题</span>
              <input
                disabled={!isAuthenticated}
                onChange={(event) => updateIdeaDraft("projectTitle", event.target.value)}
                value={draft.projectTitle}
              />
            </label>
            <label className="field creation-draft-field">
              <span>类型 / 风格</span>
              <input
                disabled={!isAuthenticated}
                onChange={(event) => updateIdeaDraft("genreStyle", event.target.value)}
                value={draft.genreStyle}
              />
            </label>
            <label className="field creation-draft-field">
              <span>目标集数</span>
              <input
                disabled={!isAuthenticated}
                min={1}
                onChange={(event) => updateIdeaDraft("episodeCount", Number(event.target.value) || 1)}
                type="number"
                value={draft.episodeCount}
              />
            </label>
          </div>

          <label className="field field-wide creation-draft-field">
            <span>灵感内容</span>
            <textarea
              disabled={!isAuthenticated}
              onChange={(event) => updateIdeaDraft("ideaText", event.target.value)}
              placeholder="例如：一个失意编剧在旧电影院发现父亲留下的未完成剧本，每一页都指向一段被隐藏的真相。"
              rows={5}
              value={draft.ideaText}
            />
          </label>

          <label className="field field-wide creation-draft-field">
            <span>额外要求</span>
            <textarea
              disabled={!isAuthenticated}
              onChange={(event) => updateIdeaDraft("extraRequirements", event.target.value)}
              placeholder="例如：节奏更紧，前 30 秒必须有强钩子，每集结尾留反转。"
              rows={3}
              value={draft.extraRequirements}
            />
          </label>
        </div>

        <div className="creation-draft-actions">
          <div className="export-actions">
            <button
              className="primary-button"
              disabled={!isAuthenticated}
              onClick={handleGenerateIdea}
              type="button"
            >
              生成短剧剧本
            </button>
            <button className="secondary-button" disabled type="button">
              下载 Word（生成后可用）
            </button>
          </div>
          <p>当前为本地演示结果，下一步将接入统一短剧剧本生成接口。生成短剧剧本后，可下载为 Word 文档。</p>
        </div>
      </section>
    );
  };

  const renderAdaptationForm = (mode: AdaptationMode) => {
    const isFilm = mode === "film";
    const draft = drafts[mode];

    return (
      <section className="creation-draft-panel" aria-label={isFilm ? "电影剧本改编草稿" : "小说改编草稿"}>
        <div className="creation-draft-header">
          <div className="panel-heading">
            <p>当前功能</p>
            <h2>{isFilm ? "电影剧本改编短剧本" : "小说 / 网文改编短剧本"}</h2>
          </div>
          <button className="secondary-button" onClick={() => setSelectedAdaptationMode(null)} type="button">
            返回改编类型选择
          </button>
        </div>

        <div className="creation-draft-form">
          <section className="document-action-card" aria-label="文档导入与导出">
            <div>
              <h3>Word 文档</h3>
              <p>支持 .docx 剧本 / 小说文档（即将接入）。当前可先粘贴文本进入改编草稿。</p>
            </div>
            <div className="document-action-row">
              <button
                className="secondary-button document-action-button"
                disabled={!isAuthenticated}
                onClick={handlePendingWordUpload}
                type="button"
              >
                上传 Word 文档
              </button>
              <button className="secondary-button document-action-button" disabled type="button">
                下载 Word（生成后可用）
              </button>
            </div>
            <p className="document-action-note">
              生成或改编完成后可导出为 Word 文档。Word 导出将在文档导出闭环接入。
            </p>
            {documentActionNotice && <p className="copy-status">{documentActionNotice}</p>}
          </section>

          <div className="creation-draft-grid">
            <label className="field creation-draft-field">
              <span>项目标题</span>
              <input
                disabled={!isAuthenticated}
                onChange={(event) => updateAdaptationDraft(mode, "projectTitle", event.target.value)}
                value={draft.projectTitle}
              />
            </label>
            <label className="field creation-draft-field">
              <span>{isFilm ? "原片 / 原剧本标题" : "原小说 / 文本标题"}</span>
              <input
                disabled={!isAuthenticated}
                onChange={(event) => updateAdaptationDraft(mode, "sourceTitle", event.target.value)}
                value={draft.sourceTitle}
              />
            </label>
            <label className="field creation-draft-field">
              <span>目标集数</span>
              <input
                disabled={!isAuthenticated}
                min={1}
                onChange={(event) => updateAdaptationDraft(mode, "episodeCount", Number(event.target.value) || 1)}
                type="number"
                value={draft.episodeCount}
              />
            </label>
          </div>

          <label className="field field-wide creation-draft-field">
            <span>{isFilm ? "剧本内容" : "小说 / 网文内容"}</span>
            <textarea
              disabled={!isAuthenticated}
              onChange={(event) => updateAdaptationDraft(mode, "sourceText", event.target.value)}
              placeholder={
                isFilm
                  ? "粘贴安全虚构的电影剧本、长剧本或分场文本。"
                  : "粘贴安全虚构的小说、网文或故事文本。"
              }
              rows={6}
              value={draft.sourceText}
            />
          </label>

          <label className="field field-wide creation-draft-field">
            <span>{isFilm ? "改编重点" : "人物与剧情改编重点"}</span>
            <textarea
              disabled={!isAuthenticated}
              onChange={(event) => updateAdaptationDraft(mode, "focus", event.target.value)}
              placeholder={
                isFilm
                  ? "例如：压缩长铺垫，保留父女主线和旧案反转。"
                  : "例如：突出人物关系、误会、选择和每集结尾钩子。"
              }
              rows={3}
              value={draft.focus}
            />
          </label>

          <label className="field field-wide creation-draft-field">
            <span>额外要求</span>
            <textarea
              disabled={!isAuthenticated}
              onChange={(event) => updateAdaptationDraft(mode, "extraRequirements", event.target.value)}
              rows={3}
              value={draft.extraRequirements}
            />
          </label>
        </div>

        <div className="creation-draft-actions">
          <button
            className="primary-button"
            disabled={!isAuthenticated}
            onClick={() => handleGenerateAdaptation(mode)}
            type="button"
          >
            生成改编短剧本
          </button>
          <p>当前为本地演示结果，下一步将接入统一短剧剧本生成接口。</p>
        </div>
      </section>
    );
  };

  return (
    <>
      <section className="product-hero" aria-label="Dramora 剧本创作工作台">
        <div className="product-hero-content">
          <p className="eyebrow">剧本创作工作台</p>
          <h1>Dramora｜剧作工坊</h1>
          <p className="subtitle">短剧剧本生成与改编工作台</p>
          <p className="description">
            从一句灵感、电影剧本或小说文本出发，生成适合短剧创作的结构化剧本。
          </p>
        </div>

        <aside className="product-hero-note" aria-label="登录状态">
          <span>{isAuthenticated ? "已登录" : "浏览模式"}</span>
          <strong>{isAuthenticated ? "可以开始创作" : "登录后可开始创作"}</strong>
          <p>{isAuthenticated ? "请选择创作方式并填写草稿。" : "当前页面可浏览，操作需要先登录。"}</p>
        </aside>
      </section>

      <CreativeModelPanel
        disabled={!isAuthenticated}
        onChange={setSelectedCreativeModel}
        selectedModel={selectedCreativeModel}
      />

      {!selectedMode && renderPrimaryCards()}
      {selectedMode === "idea" && renderIdeaForm()}
      {selectedMode === "adaptation" && !selectedAdaptationMode && renderAdaptationChoices()}
      {selectedMode === "adaptation" && selectedAdaptationMode && renderAdaptationForm(selectedAdaptationMode)}
      <ShortDramaScriptResult
        isLocked={!isAuthenticated}
        generatedAt={shortDramaGeneratedAt}
        modelLabel={buildModelLabel(selectedCreativeModel)}
        onCopyJson={handleCopyShortDramaJson}
        onDownloadJson={handleDownloadShortDramaJson}
        onDownloadTxt={handleDownloadShortDramaTxt}
        result={shortDramaResult}
        sourceLabel={shortDramaSourceLabel}
      />
    </>
  );
}
