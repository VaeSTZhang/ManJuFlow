import { useState } from "react";
import { previewDocumentImport } from "../../api/documentImport";
import { parseApiErrorMessage } from "../../api/errors";
import { generateShortDramaScript } from "../../api/scriptGeneration";
import {
  CreativeModelPanel,
  type SelectedCreativeModel,
} from "../ai/CreativeModelPanel";
import {
  buildFilmScriptGenerationInput,
  buildIdeaGenerationInput,
  buildNovelGenerationInput,
} from "./scriptGenerationRequestBuilder";
import { ShortDramaScriptResult } from "./ShortDramaScriptResult";
import type { DocumentImportOutput } from "../../types/documentImport";
import type { ShortDramaGenerationInput, ShortDramaScriptOutput } from "../../types/scriptGeneration";

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

type DocumentImportDraftState = {
  filename: string;
  text: string;
  preview: DocumentImportOutput | null;
  error: string;
  isLoading: boolean;
};

type DocumentImportDraftsByMode = Record<AdaptationMode, DocumentImportDraftState>;

type CreationHomeProps = {
  isAuthenticated: boolean;
  onRequireLogin: () => void;
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

const defaultDocumentImportDraftState: DocumentImportDraftState = {
  filename: "",
  text: "",
  preview: null,
  error: "",
  isLoading: false,
};

const defaultDocumentImportDrafts: DocumentImportDraftsByMode = {
  film: { ...defaultDocumentImportDraftState },
  novel: { ...defaultDocumentImportDraftState },
};

function buildModelLabel(selectedModel: SelectedCreativeModel): string {
  return selectedModel.model ? `${selectedModel.label} / ${selectedModel.model}` : selectedModel.label;
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
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [scriptGenerationError, setScriptGenerationError] = useState("");
  const [documentImportDrafts, setDocumentImportDrafts] =
    useState<DocumentImportDraftsByMode>(defaultDocumentImportDrafts);

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

  const updateDocumentImportDraft = (
    mode: AdaptationMode,
    patch: Partial<DocumentImportDraftState>,
  ) => {
    setDocumentImportDrafts((current) => ({
      ...current,
      [mode]: {
        ...current[mode],
        ...patch,
      },
    }));
  };

  const clearDocumentImportPreview = (mode: AdaptationMode) => {
    updateDocumentImportDraft(mode, {
      preview: null,
      error: "",
    });
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

  const setGeneratedResult = (
    result: ShortDramaScriptOutput,
    sourceLabel: string,
    requestInput: ShortDramaGenerationInput,
  ) => {
    setShortDramaResult({
      ...result,
      metadata: {
        ...result.metadata,
        prepared_request: requestInput,
      },
    });
    setShortDramaSourceLabel(sourceLabel);
    setShortDramaGeneratedAt(new Date().toLocaleString("zh-CN"));
    setScriptGenerationError("");
  };

  const runScriptGeneration = async (
    requestInput: ShortDramaGenerationInput,
    sourceLabel: string,
  ) => {
    setIsGeneratingScript(true);
    setScriptGenerationError("");

    try {
      const result = await generateShortDramaScript(requestInput);
      setGeneratedResult(result, sourceLabel, requestInput);
    } catch (error) {
      setScriptGenerationError(
        parseApiErrorMessage(error, "剧本生成失败，请确认服务已启动。"),
      );
    } finally {
      setIsGeneratingScript(false);
    }
  };

  const handleGenerateIdea = async () => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    const draft = drafts.idea;
    const sourceLabel = "灵感生成";
    const requestInput = buildIdeaGenerationInput(draft, selectedCreativeModel);

    await runScriptGeneration(requestInput, sourceLabel);
  };

  const handleGenerateAdaptation = async (mode: AdaptationMode) => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    const draft = drafts[mode];
    const isFilm = mode === "film";
    const sourceLabel = isFilm ? "电影剧本改编" : "小说 / 网文改编";
    const requestInput = isFilm
      ? buildFilmScriptGenerationInput(draft, selectedCreativeModel)
      : buildNovelGenerationInput(draft, selectedCreativeModel);

    await runScriptGeneration(requestInput, sourceLabel);
  };

  const handleGenerateDocumentImportPreview = async (mode: AdaptationMode) => {
    if (!isAuthenticated) {
      onRequireLogin();
      return;
    }

    const importDraft = documentImportDrafts[mode];
    const filename = importDraft.filename.trim();
    const extractedText = importDraft.text.trim();

    if (!filename) {
      updateDocumentImportDraft(mode, { error: "请先填写文件名。" });
      return;
    }

    if (!extractedText) {
      updateDocumentImportDraft(mode, { error: "请先粘贴文档文本。" });
      return;
    }

    const draft = drafts[mode];
    updateDocumentImportDraft(mode, {
      isLoading: true,
      error: "",
    });

    try {
      const preview = await previewDocumentImport({
        filename,
        extracted_text: extractedText,
        source_type: mode === "novel" ? "novel" : "docx",
        project_title: draft.projectTitle.trim() || draft.sourceTitle.trim() || null,
      });
      updateDocumentImportDraft(mode, { preview });
    } catch (error) {
      updateDocumentImportDraft(mode, {
        error: parseApiErrorMessage(
          error,
          "生成文档导入预览失败，请确认服务已启动。",
        ),
      });
    } finally {
      updateDocumentImportDraft(mode, { isLoading: false });
    }
  };

  const applyDocumentImportPreview = (mode: AdaptationMode, action: "fill" | "append" | "cancel") => {
    if (action === "cancel") {
      clearDocumentImportPreview(mode);
      return;
    }

    const importDraft = documentImportDrafts[mode];

    if (!importDraft.preview) {
      return;
    }

    const importedText = importDraft.preview.preview.extracted_text;

    updateAdaptationDraft(
      mode,
      "sourceText",
      action === "fill"
        ? importedText
        : [drafts[mode].sourceText.trim(), importedText].filter(Boolean).join("\n\n"),
    );
    clearDocumentImportPreview(mode);
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
        shortDramaSourceLabel ?? "系统默认",
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
              disabled={!isAuthenticated || isGeneratingScript}
              onClick={handleGenerateIdea}
              type="button"
            >
              {isGeneratingScript ? "生成中..." : "生成短剧剧本"}
            </button>
            <button className="secondary-button" disabled type="button">
              下载 Word（生成后可用）
            </button>
          </div>
          <p>当前将使用所选创作模型生成短剧剧本。生成后可复制、下载或继续进入 Word 导出流程。</p>
          {scriptGenerationError && <p className="form-error">{scriptGenerationError}</p>}
        </div>
      </section>
    );
  };

  const renderAdaptationForm = (mode: AdaptationMode) => {
    const isFilm = mode === "film";
    const draft = drafts[mode];
    const importDraft = documentImportDrafts[mode];
    const activeImportPreview = importDraft.preview;

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
              支持电影剧本、小说、网文或长文本。导入后请检查文本内容，并补充改编方向。
            </p>
            {documentActionNotice && <p className="copy-status">{documentActionNotice}</p>}
          </section>

          <section className="document-import-panel" aria-label="文档导入预览">
            <div>
              <h3>导入剧本文档内容</h3>
              <p>
                先粘贴文档解析出的文本生成预览，确认后再填入待改编文本。上传 Word 文件将在后续版本接入。
              </p>
            </div>

            <div className="document-import-grid">
              <label className="field creation-draft-field">
                <span>文件名</span>
                <input
                  disabled={!isAuthenticated || importDraft.isLoading}
                  onChange={(event) => {
                    updateDocumentImportDraft(mode, {
                      filename: event.target.value,
                      error: "",
                    });
                  }}
                  placeholder={isFilm ? "example-film-script.docx" : "example-novel.docx"}
                  value={importDraft.filename}
                />
              </label>
              <label className="field creation-draft-field">
                <span>文档文本</span>
                <textarea
                  disabled={!isAuthenticated || importDraft.isLoading}
                  onChange={(event) => {
                    updateDocumentImportDraft(mode, {
                      text: event.target.value,
                      error: "",
                    });
                  }}
                  placeholder={
                    isFilm
                      ? "粘贴电影剧本、长剧本或分场文本，生成预览后再确认填入。"
                      : "粘贴小说、网文、故事片段或人物小传，生成预览后再确认填入。"
                  }
                  rows={5}
                  value={importDraft.text}
                />
              </label>
            </div>

            <div className="document-import-actions">
              <button
                className="secondary-button"
                disabled={!isAuthenticated || importDraft.isLoading}
                onClick={() => handleGenerateDocumentImportPreview(mode)}
                type="button"
              >
                {importDraft.isLoading ? "生成预览中..." : "生成导入预览"}
              </button>
            </div>

            {importDraft.error && <p className="form-error">{importDraft.error}</p>}

            {activeImportPreview && (
              <article className="document-import-preview">
                <div className="document-import-preview-header">
                  <div>
                    <span>文档导入预览</span>
                    <strong>{activeImportPreview.preview.detected_title || "未识别标题"}</strong>
                  </div>
                  <small>{activeImportPreview.preview.source.filename}</small>
                </div>

                <dl className="document-import-preview-meta">
                  <div>
                    <dt>字数</dt>
                    <dd>{activeImportPreview.preview.character_count}</dd>
                  </div>
                  <div>
                    <dt>段落数</dt>
                    <dd>{activeImportPreview.preview.paragraph_count ?? 0}</dd>
                  </div>
                </dl>

                {activeImportPreview.preview.warnings.length > 0 && (
                  <div className="document-import-warning">
                    {activeImportPreview.preview.warnings.map((warning) => (
                      <p key={warning}>{warning}</p>
                    ))}
                  </div>
                )}

                <p className="document-import-preview-text">{activeImportPreview.preview.preview_text}</p>

                <div className="document-import-actions">
                  <button
                    className="primary-button"
                    disabled={!isAuthenticated}
                    onClick={() => applyDocumentImportPreview(mode, "fill")}
                    type="button"
                  >
                    填入待改编文本
                  </button>
                  <button
                    className="secondary-button"
                    disabled={!isAuthenticated}
                    onClick={() => applyDocumentImportPreview(mode, "append")}
                    type="button"
                  >
                    追加到当前文本后
                  </button>
                  <button
                    className="secondary-button"
                    disabled={!isAuthenticated}
                    onClick={() => applyDocumentImportPreview(mode, "cancel")}
                    type="button"
                  >
                    取消导入
                  </button>
                </div>
              </article>
            )}
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
            <span>{isFilm ? "原剧本 / 长文本内容" : "小说 / 网文 / 故事文本"}</span>
            <textarea
              disabled={!isAuthenticated}
              onChange={(event) => updateAdaptationDraft(mode, "sourceText", event.target.value)}
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
              onChange={(event) => updateAdaptationDraft(mode, "focus", event.target.value)}
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
              onChange={(event) => updateAdaptationDraft(mode, "extraRequirements", event.target.value)}
              rows={3}
              value={draft.extraRequirements}
            />
          </label>
        </div>

        <div className="creation-draft-actions">
          <button
            className="primary-button"
            disabled={!isAuthenticated || isGeneratingScript}
            onClick={() => handleGenerateAdaptation(mode)}
            type="button"
          >
            {isGeneratingScript ? "改编中..." : "生成改编短剧本"}
          </button>
          <p>文本改编将复用所选创作模型完成短剧化处理。</p>
          {scriptGenerationError && <p className="form-error">{scriptGenerationError}</p>}
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
