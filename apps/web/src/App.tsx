import { useEffect, useState } from "react";
import { useAppAuth } from "./app/useAppAuth";
import { useAppToasts } from "./app/useAppToasts";
import { useImageGenerationWorkspace } from "./app/useImageGenerationWorkspace";
import { useImagePromptWorkspace } from "./app/useImagePromptWorkspace";
import { useLegacyIdeaScriptWorkspace } from "./app/useLegacyIdeaScriptWorkspace";
import { useStoryboardWorkspace } from "./app/useStoryboardWorkspace";
import { useWorkspaceNavigation } from "./app/useWorkspaceNavigation";
import "./App.css";
import { AppShell } from "./components/layout/AppShell";
import { CharacterCountHint } from "./components/common/CharacterCountHint";
import { CreationHome } from "./components/creation/CreationHome";
import { Sidebar } from "./components/layout/Sidebar";
import { Toast } from "./components/layout/Toast";
import {
  ScriptSegmentationWorkspace,
  type ScriptSegmentationStoryboardPayload,
} from "./components/workspaces/ScriptSegmentationWorkspace";
import type { SidebarItem } from "./components/layout/Sidebar";

type SystemStatus = {
  app_name: string;
  app_env: string;
  script_generation_mode: string;
  llm_enabled: boolean;
  status: string;
};

const sidebarItems: SidebarItem[] = [
  {
    id: "creation-home",
    label: "剧本创作",
    description: "生成 / 改编",
  },
  {
    id: "script-segmentation",
    label: "剧本改编",
    description: "文本整理 / 短剧化",
  },
];

function App() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isSystemConnected, setIsSystemConnected] = useState(false);
  const { toastMessages, pushToast, dismissToast } = useAppToasts();
  const {
    isAuthenticated,
    authContext,
    isAuthLoading,
    handleLogin,
    handleLogout,
    requireLogin,
  } = useAppAuth({ pushToast });
  const {
    activeWorkspaceId,
    setActiveWorkspaceId,
    handleWorkspaceChange,
    isBrowsingMode,
  } = useWorkspaceNavigation({
    isAuthenticated,
    onRequireLogin: requireLogin,
  });

  const {
    imageGenerationForm,
    imageGenerationPromptItemsText,
    imageGenerationLoading,
    imageGenerationError,
    imageGenerationResult,
    imageGenerationBundleLoading,
    imageGenerationBundleError,
    imageGenerationBundleResult,
    updateImageGenerationField,
    updateImageGenerationPromptItemsText,
    applyImagePromptPayloadToGeneration,
    handleImageGenerationSubmit,
    handleGenerateImageBundleFromManualInput,
    handleMissingImagePromptForTransfer,
    generateImagesFromImagePromptPayload,
    generateImageBundleFromImagePromptPayload,
  } = useImageGenerationWorkspace({
    pushToast,
    onOpenImageGenerationWorkspace: () => setActiveWorkspaceId("image-generation"),
  });

  const {
    imagePromptForm,
    imagePromptResult,
    imagePromptLoading,
    imagePromptError,
    imagePromptTransferStatus,
    imagePromptCopyStatus,
    imagePromptExportStatus,
    imagePromptModelOptions,
    selectedImagePromptModel,
    updateImagePromptField,
    updateImagePromptModel,
    setImagePromptFromStoryboard,
    handleImagePromptSubmit,
    copyImagePromptJson,
    exportImagePromptJson,
    getImagePromptGenerationPayload,
    transferImagePromptToImageGeneration,
  } = useImagePromptWorkspace({
    pushToast,
    onOpenImagePromptWorkspace: () => setActiveWorkspaceId("image-prompt"),
    onImagePromptReadyForGeneration: applyImagePromptPayloadToGeneration,
    onMissingImagePromptForGeneration: handleMissingImagePromptForTransfer,
  });

  const {
    storyboardForm,
    storyboardResult,
    isStoryboardLoading,
    storyboardError,
    storyboardCopyStatus,
    storyboardExportStatus,
    storyboardTransferStatus,
    updateStoryboardField,
    setStoryboardFromScript,
    clearStoryboardTransferStatus,
    handleStoryboardSubmit,
    copyStoryboardJson,
    exportStoryboardJson,
    transferStoryboardToImagePrompt,
  } = useStoryboardWorkspace({
    pushToast,
    onOpenStoryboardWorkspace: () => setActiveWorkspaceId("storyboard"),
    onStoryboardReadyForPrompt: setImagePromptFromStoryboard,
  });
  const {
    form,
    result,
    isLoading,
    error,
    copyStatus,
    exportStatus,
    isIdeaTextTooLong,
    ideaTextMaxChars,
    updateField,
    handleSubmit,
    copyJson,
    exportJson,
    transferScriptToStoryboard,
  } = useLegacyIdeaScriptWorkspace({
    isBrowsingMode,
    pushToast,
    requireLogin,
    onClearStoryboardTransferStatus: clearStoryboardTransferStatus,
    onTransferScriptToStoryboard: ({ projectTitle, scriptText }) => {
      setStoryboardFromScript({
        projectTitle,
        scriptText,
        transferStatus: "已带入分镜生成区域",
        toastDescription: "结构化剧本已带入剧本转分镜工作区。",
      });
    },
  });

  useEffect(() => {
    const loadSystemStatus = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/system/status");

        if (!response.ok) {
          throw new Error("状态请求失败");
        }

        const data = (await response.json()) as SystemStatus;
        setSystemStatus(data);
        setIsSystemConnected(true);
      } catch {
        setSystemStatus(null);
        setIsSystemConnected(false);
        pushToast("warning", "系统状态未知", "系统状态请求失败，请确认服务是否已启动。");
      }
    };

    loadSystemStatus();
  }, []);

  const applyScriptSegmentationToStoryboard = (payload: ScriptSegmentationStoryboardPayload) => {
    setStoryboardFromScript({
      projectTitle: payload.project_title,
      scriptText: payload.script_text,
      transferStatus: "已将已有剧本切分结果带入分镜生成，请确认后点击生成分镜。",
      toastDescription: "已有剧本切分结果已带入分镜生成，请确认后点击生成分镜。",
    });
  };

  const formatTaskProgress = (progress?: number | null): string => {
    if (typeof progress !== "number") {
      return "-";
    }

    return `${Math.round(progress * 100)}%`;
  };

  const renderAssetTaskDetails = () => {
    if (!imageGenerationBundleResult) {
      return (
        <div className="empty-state workspace-empty">
          暂无资产与任务，请先在图片生成中生成结果包。
        </div>
      );
    }

    return (
      <section className="image-generation-bundle-summary">
        <div className="result-summary">
          <span>结果包项目</span>
          <h3>{imageGenerationBundleResult.project_title || "未设置"}</h3>
        </div>

        <section className="image-generation-meta">
          <div>
            <span>图片结果</span>
            <strong>{imageGenerationBundleResult.image_generation?.items?.length ?? 0}</strong>
          </div>
          <div>
            <span>资产</span>
            <strong>{imageGenerationBundleResult.assets?.assets?.length ?? 0}</strong>
          </div>
          <div>
            <span>任务</span>
            <strong>{imageGenerationBundleResult.tasks?.tasks?.length ?? 0}</strong>
          </div>
          <div>
            <span>元数据来源</span>
            <strong>{String(imageGenerationBundleResult.metadata?.source ?? "未设置")}</strong>
          </div>
        </section>

        <section className="bundle-detail-section">
          <h4>资产明细</h4>
          {imageGenerationBundleResult.assets?.assets?.length ? (
            <div className="bundle-detail-list">
              {imageGenerationBundleResult.assets.assets.map((asset) => (
                <article className="bundle-detail-card asset-card" key={asset.asset_id}>
                  <div className="mock-image-placeholder compact-placeholder">
                    <strong>图片资产</strong>
                    <span>{asset.mock_url || "-"}</span>
                    <small>
                      {asset.width ?? "?"} x {asset.height ?? "?"} · {asset.shot_id || "-"} ·{" "}
                      {asset.prompt_id || "-"}
                    </small>
                  </div>

                  <div className="prompt-card-header">
                    <span>{asset.asset_id || "-"}</span>
                    <h5>{asset.status || "-"}</h5>
                  </div>

                  <dl className="prompt-detail-grid bundle-detail-grid">
                    <div>
                      <dt>资产类型</dt>
                      <dd>{asset.asset_type || "-"}</dd>
                    </div>
                    <div>
                      <dt>生成来源</dt>
                      <dd>{asset.provider || "-"}</dd>
                    </div>
                    <div>
                      <dt>Prompt 标识</dt>
                      <dd>{asset.prompt_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>镜头标识</dt>
                      <dd>{asset.shot_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>任务标识</dt>
                      <dd>{asset.task_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>图片地址</dt>
                      <dd className="code-text">{asset.mock_url || "-"}</dd>
                    </div>
                    <div>
                      <dt>资源路径</dt>
                      <dd className="code-text">{asset.local_path || "-"}</dd>
                    </div>
                    <div>
                      <dt>尺寸</dt>
                      <dd>
                        {asset.width ?? "?"} x {asset.height ?? "?"}
                      </dd>
                    </div>
                    <div>
                      <dt>种子</dt>
                      <dd>{asset.seed ?? "-"}</dd>
                    </div>
                    <div>
                      <dt>元数据来源</dt>
                      <dd>{String(asset.metadata?.source ?? "-")}</dd>
                    </div>
                  </dl>

                  {asset.notes && (
                    <div className="bundle-note">
                      <span>备注</span>
                      <p>{asset.notes}</p>
                    </div>
                  )}
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state bundle-empty-state">暂无资产</div>
          )}
        </section>

        <section className="bundle-detail-section">
          <h4>任务明细</h4>
          {imageGenerationBundleResult.tasks?.tasks?.length ? (
            <div className="bundle-detail-list">
              {imageGenerationBundleResult.tasks.tasks.map((task) => (
                <article className="bundle-detail-card task-card" key={task.task_id}>
                  <div className="prompt-card-header">
                    <span>{task.task_id || "-"}</span>
                    <h5>{task.status || "-"}</h5>
                  </div>

                  <dl className="prompt-detail-grid bundle-detail-grid">
                    <div>
                      <dt>任务类型</dt>
                      <dd>{task.task_type || "-"}</dd>
                    </div>
                    <div>
                      <dt>进度</dt>
                      <dd className="progress-text">{formatTaskProgress(task.progress)}</dd>
                    </div>
                    <div>
                      <dt>生成来源</dt>
                      <dd>{task.provider || "-"}</dd>
                    </div>
                    <div>
                      <dt>工作流</dt>
                      <dd>{task.workflow_name || "-"}</dd>
                    </div>
                    <div>
                      <dt>Prompt 标识</dt>
                      <dd>{task.prompt_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>镜头标识</dt>
                      <dd>{task.shot_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>资产标识</dt>
                      <dd className="code-text">{task.asset_ids?.length ? task.asset_ids.join(", ") : "-"}</dd>
                    </div>
                    <div>
                      <dt>错误码</dt>
                      <dd>{task.error_code || "-"}</dd>
                    </div>
                    <div>
                      <dt>错误信息</dt>
                      <dd>{task.error_message || "-"}</dd>
                    </div>
                    <div>
                      <dt>元数据来源</dt>
                      <dd>{String(task.metadata?.source ?? "-")}</dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state bundle-empty-state">暂无任务</div>
          )}
        </section>
      </section>
    );
  };

  return (
    <AppShell
      sidebar={
        <Sidebar
          activeItemId={activeWorkspaceId}
          items={sidebarItems}
          onSelect={handleWorkspaceChange}
        />
      }
      toast={<Toast messages={toastMessages} onDismiss={dismissToast} />}
      topbar={
        <div className="top-auth-bar">
          <span>{isAuthenticated ? authContext?.user.display_name ?? "内部试用账号" : "浏览模式"}</span>
          <button
            className="auth-button"
            disabled={isAuthLoading}
            onClick={isAuthenticated ? handleLogout : handleLogin}
            type="button"
          >
            {isAuthLoading ? "登录中..." : isAuthenticated ? "退出登录" : "登录"}
          </button>
        </div>
      }
    >
      <main className="app">
      <div className="workspace-transition" key={activeWorkspaceId}>
      {activeWorkspaceId === "creation-home" && (
        <CreationHome
          authContext={authContext}
          isAuthenticated={isAuthenticated}
          onRequireLogin={requireLogin}
        />
      )}

      {activeWorkspaceId !== "creation-home" && !isAuthenticated && (
        <p className="login-required-hint workspace-login-hint">当前为浏览模式，登录后可操作。</p>
      )}

      {activeWorkspaceId === "idea-script" && (
        <>
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
              disabled={isBrowsingMode}
              onChange={(event) => updateField("idea_text", event.target.value)}
              rows={5}
            />
            <CharacterCountHint value={form.idea_text} maxLength={ideaTextMaxChars} />
          </label>

          <div className="field-grid">
            <label className="field">
              <span>剧本类型</span>
              <input
                value={form.script_type}
                disabled={isBrowsingMode}
                onChange={(event) => updateField("script_type", event.target.value)}
              />
            </label>

            <label className="field">
              <span>类型风格</span>
              <input
                value={form.genre}
                disabled={isBrowsingMode}
                onChange={(event) => updateField("genre", event.target.value)}
              />
            </label>

            <label className="field">
              <span>集数</span>
              <input
                min={1}
                type="number"
                value={form.episode_count}
                disabled={isBrowsingMode}
                onChange={(event) => updateField("episode_count", Number(event.target.value) || 1)}
              />
            </label>

            <label className="field">
              <span>单集时长</span>
              <input
                value={form.episode_duration}
                disabled={isBrowsingMode}
                onChange={(event) => updateField("episode_duration", event.target.value)}
              />
            </label>

            <label className="field">
              <span>目标平台</span>
              <input
                value={form.target_platform}
                disabled={isBrowsingMode}
                onChange={(event) => updateField("target_platform", event.target.value)}
              />
            </label>

            <label className="field">
              <span>目标受众</span>
              <input
                value={form.audience}
                disabled={isBrowsingMode}
                onChange={(event) => updateField("audience", event.target.value)}
              />
            </label>
          </div>

          <label className="field field-wide">
            <span>风格语气</span>
            <input
              value={form.tone}
              disabled={isBrowsingMode}
              onChange={(event) => updateField("tone", event.target.value)}
            />
          </label>

          <label className="field field-wide">
            <span>额外要求</span>
            <input
              value={form.style_requirements}
              disabled={isBrowsingMode}
              onChange={(event) => updateField("style_requirements", event.target.value)}
            />
          </label>

          {isIdeaTextTooLong && <p className="error-message">灵感内容已超出 5,000 字，请删减后再生成。</p>}

          <button className="primary-button" disabled={isBrowsingMode || isLoading || isIdeaTextTooLong} type="submit">
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
              <button className="secondary-button" disabled={isBrowsingMode || !result} onClick={transferScriptToStoryboard} type="button">
                带入分镜生成
              </button>
              <button className="secondary-button" disabled={isBrowsingMode || !result} onClick={copyJson} type="button">
                复制 JSON
              </button>
              <button className="secondary-button" disabled={isBrowsingMode || !result} onClick={exportJson} type="button">
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
        </>
      )}

      {activeWorkspaceId === "storyboard" && (
      <section className="storyboard-workspace">
        <form className="panel form-panel" onSubmit={handleStoryboardSubmit}>
          <div className="panel-heading">
            <p>分镜工作区</p>
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
                带入绘图 Prompt 生成
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
      )}

      {activeWorkspaceId === "script-segmentation" && (
        <ScriptSegmentationWorkspace
          initialProjectTitle={result?.project_title || storyboardForm.project_title}
          isLocked={isBrowsingMode}
          onApplyToStoryboard={applyScriptSegmentationToStoryboard}
          onNotify={pushToast}
        />
      )}

      {activeWorkspaceId === "image-prompt" && (
      <section className="image-prompt-workspace" id="image-prompt-workspace">
        <form className="panel form-panel" onSubmit={handleImagePromptSubmit}>
          <div className="panel-heading">
            <p>提示词工作区</p>
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
            <span>分镜摘要</span>
            <textarea
              value={imagePromptForm.storyboard_summary || ""}
              onChange={(event) => updateImagePromptField("storyboard_summary", event.target.value)}
              rows={3}
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
              <span>LLM 模型</span>
              <select value={selectedImagePromptModel.value} onChange={(event) => updateImagePromptModel(event.target.value)}>
                {imagePromptModelOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

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
                <option value="9:16">竖屏 9:16</option>
                <option value="16:9">横屏 16:9</option>
                <option value="1:1">方图 1:1</option>
                <option value="4:5">竖图 4:5</option>
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
              <span>Prompt 输出语言</span>
              <select
                value={imagePromptForm.language || "en"}
                onChange={(event) => updateImagePromptField("language", event.target.value)}
              >
                <option value="en">英文</option>
                <option value="zh">中文</option>
              </select>
              <small className="field-help-text">
                英文 Prompt 更适合部分绘图模型；中文 Prompt 方便团队审阅和内部沟通。
              </small>
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

          <div className="model-selection-note">
            <strong>
              当前模型：
              {selectedImagePromptModel.provider
                ? ` ${selectedImagePromptModel.label}`
                : " 系统默认模型"}
            </strong>
            <p>模型选择在绘图 Prompt 生成时生效。</p>
          </div>

          <button className="primary-button" disabled={imagePromptLoading} type="submit">
            {imagePromptLoading ? "生成中..." : "生成绘图 Prompt"}
          </button>

          {imagePromptError && <p className="error-message">{imagePromptError}</p>}
          {imagePromptTransferStatus && <p className="copy-status">{imagePromptTransferStatus}</p>}
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
                onClick={transferImagePromptToImageGeneration}
                type="button"
              >
                带入图片生成
              </button>
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
                        <span>正向 Prompt</span>
                        <p>{item.positive_prompt}</p>
                      </div>

                      <div className="prompt-text-block negative-prompt">
                        <span>反向 Prompt</span>
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
      )}

      {activeWorkspaceId === "image-generation" && (
      <section className="image-generation-workspace">
        <form className="panel form-panel" onSubmit={handleImageGenerationSubmit}>
          <div className="panel-heading">
            <p>图片生成工作区</p>
            <h2>生成图片</h2>
          </div>

          <label className="field field-wide">
            <span>项目标题</span>
            <input
              value={imageGenerationForm.project_title}
              onChange={(event) => updateImageGenerationField("project_title", event.target.value)}
            />
          </label>

          <div className="field-grid">
            <label className="field">
              <span>生成来源</span>
              <select
                value={imageGenerationForm.provider || "mock"}
                onChange={(event) => updateImageGenerationField("provider", event.target.value)}
              >
                <option value="mock">系统生成</option>
              </select>
            </label>

            <label className="field">
              <span>工作流</span>
              <input
                value={imageGenerationForm.workflow_name || "system_image_generation_v1"}
                onChange={(event) => updateImageGenerationField("workflow_name", event.target.value)}
              />
            </label>

            <label className="field">
              <span>画面比例</span>
              <select
                value={imageGenerationForm.aspect_ratio || "9:16"}
                onChange={(event) => updateImageGenerationField("aspect_ratio", event.target.value)}
              >
                <option value="9:16">竖屏 9:16</option>
                <option value="16:9">横屏 16:9</option>
                <option value="1:1">方图 1:1</option>
              </select>
            </label>

            <label className="field">
              <span>生成数量</span>
              <input
                max={4}
                min={1}
                type="number"
                value={imageGenerationForm.output_count || 1}
                onChange={(event) =>
                  updateImageGenerationField("output_count", Number(event.target.value) || 1)
                }
              />
            </label>

            <label className="field">
              <span>风格预设</span>
              <input
                value={imageGenerationForm.style_preset || "cinematic realistic"}
                onChange={(event) => updateImageGenerationField("style_preset", event.target.value)}
              />
            </label>

            <label className="field">
              <span>种子</span>
              <input
                type="number"
                value={imageGenerationForm.seed ?? ""}
                onChange={(event) =>
                  updateImageGenerationField(
                    "seed",
                    event.target.value === "" ? null : Number(event.target.value),
                  )
                }
              />
            </label>
          </div>

          <label className="field field-wide">
            <span>prompt_items JSON</span>
            <textarea
              value={imageGenerationPromptItemsText}
              onChange={(event) => updateImageGenerationPromptItemsText(event.target.value)}
              rows={9}
            />
          </label>

          <button
            className="secondary-button"
            disabled={!imagePromptResult?.items.length || imageGenerationLoading}
            onClick={() => generateImagesFromImagePromptPayload(getImagePromptGenerationPayload())}
            type="button"
          >
            使用绘图 Prompt 结果生成图片
          </button>

          <button
            className="secondary-button"
            disabled={!imagePromptResult?.items.length || imageGenerationBundleLoading}
            onClick={() => generateImageBundleFromImagePromptPayload(getImagePromptGenerationPayload())}
            type="button"
          >
            使用绘图 Prompt 结果生成结果包
          </button>

          <button
            className="secondary-button"
            disabled={imageGenerationBundleLoading}
            onClick={handleGenerateImageBundleFromManualInput}
            type="button"
          >
            {imageGenerationBundleLoading ? "生成结果包中..." : "生成结果包（图片 + 资产 + 任务）"}
          </button>

          <button className="primary-button" disabled={imageGenerationLoading} type="submit">
            {imageGenerationLoading ? "生成中..." : "生成图片"}
          </button>

          {imageGenerationError && <p className="error-message">{imageGenerationError}</p>}
          {imageGenerationBundleError && <p className="error-message">{imageGenerationBundleError}</p>}
        </form>

        <section className="panel result-panel">
          <div className="result-header">
            <div>
              <p>输出预览</p>
              <h2>图片生成结果</h2>
            </div>
          </div>

          {imageGenerationBundleResult && (
            <section className="image-generation-bundle-summary">
              <div className="result-summary">
                <span>结果包项目</span>
                <h3>{imageGenerationBundleResult.project_title || "未设置"}</h3>
              </div>

              <section className="image-generation-meta">
                <div>
                  <span>图片结果</span>
                  <strong>{imageGenerationBundleResult.image_generation?.items?.length ?? 0}</strong>
                </div>
                <div>
                  <span>资产</span>
                  <strong>{imageGenerationBundleResult.assets?.assets?.length ?? 0}</strong>
                </div>
                <div>
                  <span>任务</span>
                  <strong>{imageGenerationBundleResult.tasks?.tasks?.length ?? 0}</strong>
                </div>
                <div>
                  <span>元数据来源</span>
                  <strong>{String(imageGenerationBundleResult.metadata?.source ?? "未设置")}</strong>
                </div>
                <div>
                  <span>生成来源</span>
                  <strong>{String(imageGenerationBundleResult.metadata?.provider ?? "未设置")}</strong>
                </div>
                <div>
                  <span>结果包版本</span>
                  <strong>{String(imageGenerationBundleResult.metadata?.bundle_version ?? "未设置")}</strong>
                </div>
              </section>

              <section className="bundle-detail-section">
                <h4>资产明细</h4>
                {imageGenerationBundleResult.assets?.assets?.length ? (
                  <div className="bundle-detail-list">
                    {imageGenerationBundleResult.assets.assets.map((asset) => (
                      <article className="bundle-detail-card asset-card" key={asset.asset_id}>
                        <div className="mock-image-placeholder compact-placeholder">
                          <strong>图片资产</strong>
                          <span>{asset.mock_url || "-"}</span>
                          <small>
                            {asset.width ?? "?"} x {asset.height ?? "?"} · {asset.shot_id || "-"} ·{" "}
                            {asset.prompt_id || "-"}
                          </small>
                        </div>

                        <div className="prompt-card-header">
                          <span>{asset.asset_id || "-"}</span>
                          <h5>{asset.status || "-"}</h5>
                        </div>

                        <dl className="prompt-detail-grid bundle-detail-grid">
                          <div>
                            <dt>资产类型</dt>
                            <dd>{asset.asset_type || "-"}</dd>
                          </div>
                          <div>
                            <dt>生成来源</dt>
                            <dd>{asset.provider || "-"}</dd>
                          </div>
                          <div>
                            <dt>Prompt 标识</dt>
                            <dd>{asset.prompt_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>镜头标识</dt>
                            <dd>{asset.shot_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>任务标识</dt>
                            <dd>{asset.task_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>尺寸</dt>
                            <dd>
                              {asset.width ?? "?"} x {asset.height ?? "?"}
                            </dd>
                          </div>
                          <div>
                            <dt>种子</dt>
                            <dd>{asset.seed ?? "-"}</dd>
                          </div>
                          <div>
                            <dt>元数据来源</dt>
                            <dd>{String(asset.metadata?.source ?? "-")}</dd>
                          </div>
                          <div>
                            <dt>图片地址</dt>
                            <dd className="code-text">{asset.mock_url || "-"}</dd>
                          </div>
                          <div>
                            <dt>资源路径</dt>
                            <dd className="code-text">{asset.local_path || "-"}</dd>
                          </div>
                        </dl>

                        {asset.notes && (
                          <div className="bundle-note">
                            <span>备注</span>
                            <p>{asset.notes}</p>
                          </div>
                        )}
                      </article>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state bundle-empty-state">暂无资产</div>
                )}
              </section>

              <section className="bundle-detail-section">
                <h4>任务明细</h4>
                {imageGenerationBundleResult.tasks?.tasks?.length ? (
                  <div className="bundle-detail-list">
                    {imageGenerationBundleResult.tasks.tasks.map((task) => (
                      <article className="bundle-detail-card task-card" key={task.task_id}>
                        <div className="prompt-card-header">
                          <span>{task.task_id || "-"}</span>
                          <h5>{task.status || "-"}</h5>
                        </div>

                        <dl className="prompt-detail-grid bundle-detail-grid">
                          <div>
                            <dt>任务类型</dt>
                            <dd>{task.task_type || "-"}</dd>
                          </div>
                          <div>
                            <dt>进度</dt>
                            <dd className="progress-text">{formatTaskProgress(task.progress)}</dd>
                          </div>
                          <div>
                            <dt>生成来源</dt>
                            <dd>{task.provider || "-"}</dd>
                          </div>
                          <div>
                            <dt>工作流</dt>
                            <dd>{task.workflow_name || "-"}</dd>
                          </div>
                          <div>
                            <dt>Prompt 标识</dt>
                            <dd>{task.prompt_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>镜头标识</dt>
                            <dd>{task.shot_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>资产标识</dt>
                            <dd className="code-text">{task.asset_ids?.length ? task.asset_ids.join(", ") : "-"}</dd>
                          </div>
                          <div>
                            <dt>错误码</dt>
                            <dd>{task.error_code || "-"}</dd>
                          </div>
                          <div>
                            <dt>元数据来源</dt>
                            <dd>{String(task.metadata?.source ?? "-")}</dd>
                          </div>
                        </dl>

                        {(task.status === "failed" || task.error_message) && (
                          <div className="bundle-note task-error-note">
                            <span>错误信息</span>
                            <p>{task.error_message || "-"}</p>
                          </div>
                        )}
                      </article>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state bundle-empty-state">暂无任务</div>
                )}
              </section>
            </section>
          )}

          {!imageGenerationResult ? (
            <div className="empty-state">图片生成结果将在这里展示。</div>
          ) : (
            <article className="script-output image-generation-output">
              <section className="result-summary">
                <span>项目标题</span>
                <h3>{imageGenerationResult.project_title}</h3>
              </section>

              <section className="image-generation-meta">
                <div>
                  <span>生成来源</span>
                  <strong>{imageGenerationResult.provider}</strong>
                </div>
                <div>
                  <span>状态</span>
                  <strong>{imageGenerationResult.status}</strong>
                </div>
                <div>
                  <span>条目数量</span>
                  <strong>{imageGenerationResult.items.length}</strong>
                </div>
              </section>

              <section className="image-generation-items">
                <h4>图片生成结果</h4>
                <div className="image-generation-list">
                  {imageGenerationResult.items.map((item) => (
                    <section className="image-generation-card" key={item.task_id}>
                      <div className="mock-image-placeholder">
                        <strong>图片结果</strong>
                        <span>{item.mock_url || "图片结果待生成"}</span>
                        <small>
                          {item.width ?? "?"} x {item.height ?? "?"} · {item.shot_id} · {item.prompt_id}
                        </small>
                      </div>

                      <div className="prompt-card-header">
                        <span>{item.task_id}</span>
                        <h5>{item.status}</h5>
                      </div>

                      <dl className="prompt-detail-grid">
                        <div>
                          <dt>Prompt 标识</dt>
                          <dd>{item.prompt_id}</dd>
                        </div>
                        <div>
                          <dt>镜头标识</dt>
                          <dd>{item.shot_id}</dd>
                        </div>
                        <div>
                          <dt>图片地址</dt>
                          <dd>{item.mock_url || "未设置"}</dd>
                        </div>
                        <div>
                          <dt>资源路径</dt>
                          <dd>{item.local_path || "未设置"}</dd>
                        </div>
                        <div>
                          <dt>尺寸</dt>
                          <dd>
                            {item.width ?? "?"} x {item.height ?? "?"}
                          </dd>
                        </div>
                        <div>
                          <dt>种子</dt>
                          <dd>{item.seed ?? "未设置"}</dd>
                        </div>
                        <div>
                          <dt>元数据来源</dt>
                          <dd>{String(item.metadata?.source ?? "未设置")}</dd>
                        </div>
                      </dl>

                      <div className="prompt-text-block positive-prompt">
                        <span>正向 Prompt</span>
                        <p>{item.positive_prompt}</p>
                      </div>

                      <div className="prompt-text-block negative-prompt">
                        <span>反向 Prompt</span>
                        <p>{item.negative_prompt}</p>
                      </div>
                    </section>
                  ))}
                </div>
              </section>
            </article>
          )}
        </section>
      </section>
      )}

      {activeWorkspaceId === "assets-tasks" && (
        <section className="workspace-section">
          <div className="workspace-header">
            <p>资产与任务工作区</p>
            <h2>资产与任务</h2>
          </div>
          {renderAssetTaskDetails()}
        </section>
      )}

      {activeWorkspaceId === "system-status" && (
        <section className="workspace-section">
          <div className="workspace-header">
            <p>系统状态</p>
            <h2>运行状态</h2>
          </div>

          <section className="panel result-panel system-status-panel">
            <div className="system-status system-status-detail" aria-label="系统运行状态">
              <div className={isSystemConnected ? "status-dot status-ok" : "status-dot status-offline"} />
              <div>
                <p>{isSystemConnected ? `系统状态：${systemStatus?.status}` : "系统状态：未连接"}</p>
                {isSystemConnected && systemStatus ? (
                  <>
                    <p>应用名称：{systemStatus.app_name}</p>
                    <p>运行环境：{systemStatus.app_env}</p>
                    <p>生成模式：{systemStatus.script_generation_mode}</p>
                    <p>LLM：{systemStatus.llm_enabled ? "已启用" : "未启用"}</p>
                  </>
                ) : (
                  <p>请确认服务已启动。</p>
                )}
              </div>
            </div>
          </section>
        </section>
      )}
      </div>
      </main>
    </AppShell>
  );
}

export default App;
