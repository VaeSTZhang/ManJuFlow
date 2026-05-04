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
import { AdaptationDraftForm } from "./AdaptationDraftForm";
import { DocumentImportPanel } from "./DocumentImportPanel";
import { IdeaDraftForm } from "./IdeaDraftForm";
import { ShortDramaScriptResult } from "./ShortDramaScriptResult";
import {
  useDocumentImportDrafts,
} from "../../hooks/creation/useDocumentImportDrafts";
import type {
  AdaptationDraft,
  AdaptationMode,
  CreationDrafts,
  CreationMode,
  IdeaCreationDraft,
} from "./creationDraftTypes";
import type { ShortDramaGenerationInput, ShortDramaScriptOutput } from "../../types/scriptGeneration";

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
  const {
    documentImportDrafts,
    updateDocumentImportDraft,
    clearDocumentImportPreview,
  } = useDocumentImportDrafts();

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
        <p>先选择本次创作来源，再进入对应草稿区。确认内容后再开始生成。</p>
      </div>

      <div className="creation-entry-grid creation-entry-grid-two">
        <button
          className={`creation-entry-card${!isAuthenticated ? " locked" : ""}`}
          data-testid="creation-entry-card-idea"
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
          data-testid="creation-entry-card-adaptation"
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
          data-testid="creation-entry-card-film"
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
          data-testid="creation-entry-card-novel"
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

        <IdeaDraftForm draft={draft} isAuthenticated={isAuthenticated} onChange={updateIdeaDraft} />

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

        <AdaptationDraftForm
          documentActionNotice={documentActionNotice}
          documentImportPanel={
            <DocumentImportPanel
              error={importDraft.error}
              filename={importDraft.filename}
              isAuthenticated={isAuthenticated}
              isFilm={isFilm}
              isLoading={importDraft.isLoading}
              onApplyAppend={() => applyDocumentImportPreview(mode, "append")}
              onApplyFill={() => applyDocumentImportPreview(mode, "fill")}
              onCancel={() => applyDocumentImportPreview(mode, "cancel")}
              onFilenameChange={(value) => {
                updateDocumentImportDraft(mode, {
                  filename: value,
                  error: "",
                });
              }}
              onGeneratePreview={() => handleGenerateDocumentImportPreview(mode)}
              onTextChange={(value) => {
                updateDocumentImportDraft(mode, {
                  text: value,
                  error: "",
                });
              }}
              preview={importDraft.preview}
              text={importDraft.text}
            />
          }
          draft={draft}
          isAuthenticated={isAuthenticated}
          isFilm={isFilm}
          onChange={(field, value) => updateAdaptationDraft(mode, field, value)}
          onPendingWordUpload={handlePendingWordUpload}
        />

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
      <section className="product-hero" aria-label="Dramora 剧本创作工作台" data-testid="creation-home">
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
