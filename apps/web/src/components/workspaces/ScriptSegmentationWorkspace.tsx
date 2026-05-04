import { FormEvent, useState } from "react";
import { segmentScript } from "../../api/scriptSegmentation";
import { uploadScriptMock } from "../../api/uploads";
import { parseApiErrorMessage } from "../../api/errors";
import { CharacterCountHint } from "../common/CharacterCountHint";
import type {
  ExistingScriptInput,
  ScriptSegmentationOutput,
} from "../../types/scriptSegmentation";
import type { ScriptUploadOutput } from "../../types/upload";

type NotificationType = "success" | "error" | "warning" | "info";

export type ScriptSegmentationStoryboardPayload = {
  project_title: string;
  script_text: string;
};

type ScriptSegmentationWorkspaceProps = {
  initialProjectTitle?: string;
  isLocked?: boolean;
  onApplyToStoryboard: (payload: ScriptSegmentationStoryboardPayload) => void;
  onNotify?: (type: NotificationType, title: string, description?: string) => void;
};

const EXISTING_SCRIPT_MAX_CHARS = 100_000;

function createDefaultScriptSegmentationForm(projectTitle?: string): ExistingScriptInput {
  return {
    project_title: projectTitle || "测试短剧：雨夜重逢",
    script_text:
      "第1集 第1场｜医院门口｜雨夜。暴雨中，林晚撑着黑伞站在医院门口，顾沉从车里下来，两人隔雨对视。顾沉：你终于肯回来了？林晚：我回来，不是为了见你。",
    source_type: "pasted_text",
    target_segment_level: "scene",
    language: "zh",
    extra_requirements: "按短剧场景切分，保留人物、地点、冲突、情绪和可视化提示。",
    workspace_id: "mock_workspace_script_segmentation",
    user_id: "mock_user_writer_001",
    ai_account_id: "mock_ai_account_writer_001",
    metadata: {
      project_id: "mock_project_script_segmentation",
      context_policy: "current_project_only",
    },
  };
}

function sanitizeFileName(value: string): string {
  return value
    .trim()
    .replace(/[\\/:*?"<>|]/g, "-")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60);
}

function formatSourceTypeLabel(sourceType?: string | null): string {
  const sourceTypeLabels: Record<string, string> = {
    pasted_text: "粘贴文本",
    script_docx: "Word 剧本文档",
    uploaded_text: "上传文本",
  };

  if (!sourceType) {
    return "未知来源";
  }

  return sourceTypeLabels[sourceType] || "未知来源";
}

function formatScriptSegmentationForStoryboard(segmentation: ScriptSegmentationOutput): string {
  const segmentsText = segmentation.segments
    .map((segment) =>
      [
        `[${segment.segment_id}] ${segment.title}`,
        "原文：",
        segment.original_text,
        "",
        "摘要：",
        segment.summary,
        "",
        "人物：",
        segment.characters.length ? segment.characters.join("、") : "-",
        "",
        "场景：",
        `${segment.location || "-"} / ${segment.time_of_day || "-"}`,
        "",
        "冲突：",
        segment.conflict || "-",
        "",
        "情绪：",
        segment.emotion || "-",
        "",
        "视觉备注：",
        segment.visual_notes || "-",
        "",
        "对话：",
        segment.dialogue_text || "-",
      ].join("\n"),
    )
    .join("\n\n---\n\n");

  return [
    `项目标题：${segmentation.project_title}`,
    "",
    "切分摘要：",
    segmentation.segmentation_summary,
    "",
    "结构化改编素材片段：",
    segmentsText,
  ].join("\n");
}

export function ScriptSegmentationWorkspace({
  initialProjectTitle,
  isLocked = false,
  onApplyToStoryboard,
  onNotify,
}: ScriptSegmentationWorkspaceProps) {
  const [scriptSegmentationForm, setScriptSegmentationForm] = useState<ExistingScriptInput>(
    createDefaultScriptSegmentationForm(initialProjectTitle),
  );
  const [scriptSegmentationResult, setScriptSegmentationResult] =
    useState<ScriptSegmentationOutput | null>(null);
  const [scriptSegmentationLoading, setScriptSegmentationLoading] = useState(false);
  const [scriptSegmentationError, setScriptSegmentationError] = useState("");
  const [scriptSegmentationCopyStatus, setScriptSegmentationCopyStatus] = useState("");
  const [scriptSegmentationExportStatus, setScriptSegmentationExportStatus] = useState("");
  const [scriptUploadLoading, setScriptUploadLoading] = useState(false);
  const [scriptUploadError, setScriptUploadError] = useState("");
  const [scriptUploadResult, setScriptUploadResult] = useState<ScriptUploadOutput | null>(null);

  const scriptSegmentationText = scriptSegmentationForm.script_text || "";
  const isScriptSegmentationTextTooLong = scriptSegmentationText.length > EXISTING_SCRIPT_MAX_CHARS;

  const notify = (type: NotificationType, title: string, description?: string) => {
    onNotify?.(type, title, description);
  };

  const updateScriptSegmentationField = <K extends keyof ExistingScriptInput>(
    field: K,
    value: ExistingScriptInput[K],
  ) => {
    setScriptSegmentationForm((current) => ({ ...current, [field]: value }));
    setScriptSegmentationError("");
    setScriptSegmentationCopyStatus("");
    setScriptSegmentationExportStatus("");
    if (field === "script_text") {
      setScriptUploadError("");
    }
  };

  const handleScriptSegmentationSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (isLocked) {
      notify("warning", "请先登录", "请先登录后开始创作。");
      return;
    }

    if (!scriptSegmentationForm.project_title.trim()) {
      setScriptSegmentationError("请先填写项目标题。");
      notify("warning", "缺少必填项", "整理剧本素材前请先填写项目标题。");
      return;
    }

    if (!scriptSegmentationForm.script_text?.trim() && !scriptSegmentationForm.source_id?.trim()) {
      setScriptSegmentationError("请先粘贴待改编文本。");
      notify("warning", "缺少剧本文本", "请粘贴待改编文本后再执行整理。");
      return;
    }

    if (isScriptSegmentationTextTooLong) {
      setScriptSegmentationError("待改编文本已超出 100,000 字，请删减或拆分后再整理。");
      notify("warning", "文本过长", "待改编文本已超出 100,000 字，请删减或拆分后再整理。");
      return;
    }

    setScriptSegmentationLoading(true);
    setScriptSegmentationError("");
    setScriptSegmentationCopyStatus("");
    setScriptSegmentationExportStatus("");

    try {
      const data = await segmentScript({
        ...scriptSegmentationForm,
        project_title: scriptSegmentationForm.project_title.trim(),
        script_text: scriptSegmentationForm.script_text?.trim() || null,
        source_type: scriptSegmentationForm.source_type || "pasted_text",
        target_segment_level: scriptSegmentationForm.target_segment_level || "scene",
        language: scriptSegmentationForm.language || "zh",
        extra_requirements: scriptSegmentationForm.extra_requirements?.trim() || null,
        workspace_id: "mock_workspace_script_segmentation",
        user_id: "mock_user_writer_001",
        ai_account_id: "mock_ai_account_writer_001",
        metadata: {
          ...(scriptSegmentationForm.metadata || {}),
          project_id: "mock_project_script_segmentation",
          context_policy: "current_project_only",
          upload_source_id: scriptSegmentationForm.source_id || null,
        },
      });

      setScriptSegmentationResult(data);
      notify("success", "切分完成", "剧本素材已生成结构化片段。");
    } catch (error) {
      const message = parseApiErrorMessage(
        error,
        "整理剧本素材失败，请确认后端服务已启动：http://127.0.0.1:8000",
      );
      setScriptSegmentationError(message);
      notify("error", "切分失败", message);
    } finally {
      setScriptSegmentationLoading(false);
    }
  };

  const handleMockScriptUpload = async () => {
    if (isLocked) {
      notify("warning", "请先登录", "请先登录后开始创作。");
      return;
    }

    if (!scriptSegmentationForm.project_title.trim()) {
      setScriptUploadError("请先填写项目标题。");
      notify("warning", "缺少必填项", "上传 Word 文档前请先填写项目标题。");
      return;
    }

    setScriptUploadLoading(true);
    setScriptUploadError("");
    setScriptSegmentationError("");

    try {
      const data = await uploadScriptMock({
        project_title: scriptSegmentationForm.project_title.trim(),
        source_type: "script_docx",
        workspace_id: "mock_workspace_script_segmentation",
        project_id: "mock_project_script_upload",
        user_id: "mock_user_writer_001",
        ai_account_id: "mock_ai_account_writer_001",
        language: "zh",
        extra_requirements: "请提取剧本文本，并保留适合后续分镜切分的段落顺序。",
        metadata: {
          context_policy: "current_project_only",
          upload_mode: "mock_metadata_only",
        },
      });

      setScriptUploadResult(data);
      setScriptSegmentationForm((current) => ({
        ...current,
        project_title: data.project_title,
        script_text: data.extracted_text,
        source_id: data.source_id,
        source_type: data.metadata.source_type,
        workspace_id: "mock_workspace_script_segmentation",
        user_id: "mock_user_writer_001",
        ai_account_id: "mock_ai_account_writer_001",
        metadata: {
          ...(current.metadata || {}),
          project_id: "mock_project_script_segmentation",
          context_policy: "current_project_only",
          upload_source_id: data.source_id,
        },
      }));
      notify("success", "文档导入完成", "已将提取文本填入下方剧本文本框，可继续整理。");
    } catch (error) {
      const message = parseApiErrorMessage(
        error,
        "上传 Word 文档失败，请确认后端服务已启动：http://127.0.0.1:8000",
      );
      setScriptUploadError(message);
      notify("error", "上传失败", message);
    } finally {
      setScriptUploadLoading(false);
    }
  };

  const copyScriptSegmentationJson = async () => {
    if (isLocked) {
      notify("warning", "请先登录", "请先登录后开始创作。");
      return;
    }

    if (!scriptSegmentationResult) {
      return;
    }

    try {
      await navigator.clipboard.writeText(JSON.stringify(scriptSegmentationResult, null, 2));
      setScriptSegmentationCopyStatus("已复制切分 JSON");
      setScriptSegmentationExportStatus("");
      setScriptSegmentationError("");
      notify("success", "复制成功", "剧本改编素材 JSON 已复制到剪贴板。");
    } catch {
      setScriptSegmentationError("复制切分 JSON 失败，请检查浏览器剪贴板权限。");
      notify("error", "复制失败", "复制剧本改编素材 JSON 失败，请检查浏览器剪贴板权限。");
    }
  };

  const exportScriptSegmentationJson = () => {
    if (isLocked) {
      notify("warning", "请先登录", "请先登录后开始创作。");
      return;
    }

    if (!scriptSegmentationResult) {
      return;
    }

    const json = JSON.stringify(scriptSegmentationResult, null, 2);
    const blob = new Blob([json], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const safeTitle = sanitizeFileName(scriptSegmentationResult.project_title) || "output";

    link.href = url;
    link.download = `script-segments-${safeTitle}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    setScriptSegmentationExportStatus("已导出切分 JSON");
    setScriptSegmentationCopyStatus("");
    setScriptSegmentationError("");
    notify("success", "导出成功", "剧本改编素材 JSON 已导出。");
  };

  const transferScriptSegmentationToStoryboard = () => {
    if (isLocked) {
      notify("warning", "请先登录", "请先登录后开始创作。");
      return;
    }

    if (!scriptSegmentationResult || scriptSegmentationResult.segments.length === 0) {
      return;
    }

    onApplyToStoryboard({
      project_title: scriptSegmentationResult.project_title,
      script_text: formatScriptSegmentationForStoryboard(scriptSegmentationResult),
    });
  };

  return (
    <section className="script-segmentation-workspace">
      <form className="panel form-panel" onSubmit={handleScriptSegmentationSubmit}>
        <div className="panel-heading">
          <p>剧本改编</p>
          <h2>长文本整理与短剧化改编</h2>
          <span>根据原文内容和改编方向，整理为可改编、可分镜、可生成剧本的结构化素材。</span>
        </div>
        {isLocked && <p className="login-required-hint">当前为浏览模式，登录后可操作。</p>}

        <label className="field field-wide">
          <span>项目标题</span>
          <input
            value={scriptSegmentationForm.project_title}
            disabled={isLocked}
            onChange={(event) => updateScriptSegmentationField("project_title", event.target.value)}
          />
        </label>

        <section className="script-upload-mock-card">
          <div>
            <h3>上传 Word 文档</h3>
            <p>
              Word 导入能力将逐步接入；当前可先粘贴文本或使用文档导入入口。导入后请检查“待改编文本”，并补充改编方向。
            </p>
          </div>

          <button
            className="secondary-button"
            disabled={isLocked || scriptUploadLoading}
            onClick={handleMockScriptUpload}
            type="button"
          >
            {scriptUploadLoading ? "上传处理中..." : "上传 Word 文档"}
          </button>

          {scriptUploadError && <p className="error-message">{scriptUploadError}</p>}

          {scriptUploadResult && (
            <div className="script-upload-result">
              <div>
                <span>上传源标识</span>
                <strong>{scriptUploadResult.source_id}</strong>
              </div>
              <div>
                <span>提取状态</span>
                <strong>{scriptUploadResult.metadata.extraction_status}</strong>
              </div>
              <div>
                <span>提取文本长度</span>
                <strong>{scriptUploadResult.metadata.extracted_text_length}</strong>
              </div>
              <div>
                <span>来源类型</span>
                <strong>{formatSourceTypeLabel(scriptUploadResult.metadata.source_type)}</strong>
              </div>
              <p>已将提取文本填入下方待改编文本区域，请继续填写改编方向 / 额外要求。</p>
              {scriptUploadResult.warnings.length > 0 && (
                <ul className="script-upload-warnings">
                  {scriptUploadResult.warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </section>

        <label className="field field-wide">
          <span>待改编文本</span>
          <textarea
            value={scriptSegmentationForm.script_text || ""}
            disabled={isLocked}
            onChange={(event) => updateScriptSegmentationField("script_text", event.target.value)}
            placeholder="上传 Word 后会把文档内容填入这里。也可以直接粘贴待改编文本、小说片段、剧本片段或人物小传。"
            rows={10}
          />
          <CharacterCountHint value={scriptSegmentationText} maxLength={EXISTING_SCRIPT_MAX_CHARS} />
        </label>

        <div className="script-text-counter">
          {scriptSegmentationForm.source_id && <span>上传源标识：{scriptSegmentationForm.source_id}</span>}
        </div>

        {isScriptSegmentationTextTooLong && (
          <p className="error-message">待改编文本已超出 100,000 字，请删减或拆分后再整理。</p>
        )}

        <div className="field-grid">
          <label className="field">
            <span>来源类型</span>
            <select
              value={scriptSegmentationForm.source_type || "pasted_text"}
              disabled={isLocked}
              onChange={(event) => updateScriptSegmentationField("source_type", event.target.value)}
            >
              <option value="pasted_text">粘贴文本</option>
              <option value="script_docx">Word 剧本文档</option>
              <option value="uploaded_text">上传文本</option>
            </select>
          </label>

          <label className="field">
            <span>切分粒度</span>
            <select
              value={scriptSegmentationForm.target_segment_level || "scene"}
              disabled={isLocked}
              onChange={(event) => updateScriptSegmentationField("target_segment_level", event.target.value)}
            >
              <option value="scene">按场景</option>
              <option value="episode">按集</option>
              <option value="beat">按节拍</option>
            </select>
          </label>

          <label className="field">
            <span>语言</span>
            <select
              value={scriptSegmentationForm.language || "zh"}
              disabled={isLocked}
              onChange={(event) => updateScriptSegmentationField("language", event.target.value)}
            >
              <option value="zh">中文</option>
              <option value="en">英文</option>
            </select>
          </label>
        </div>

        <label className="field field-wide">
          <span>改编方向 / 额外要求</span>
          <textarea
            value={scriptSegmentationForm.extra_requirements || ""}
            disabled={isLocked}
            onChange={(event) => updateScriptSegmentationField("extra_requirements", event.target.value)}
            placeholder="请说明希望改成的短剧方向：题材、集数、主角弧光、爽点、反转、必须保留或弱化的内容。"
            rows={3}
          />
        </label>

        <button
          className="primary-button"
          disabled={isLocked || scriptSegmentationLoading || isScriptSegmentationTextTooLong}
          type="submit"
        >
          {scriptSegmentationLoading ? "整理中..." : "整理剧本素材"}
        </button>

        {scriptSegmentationError && <p className="error-message">{scriptSegmentationError}</p>}
      </form>

      <section className="panel result-panel">
        <div className="result-header">
          <div>
            <p>输出预览</p>
            <h2>剧本改编素材结果</h2>
          </div>
          <div className="result-actions">
            <button
              className="secondary-button"
              disabled={isLocked || !scriptSegmentationResult}
              onClick={copyScriptSegmentationJson}
              type="button"
            >
              复制切分 JSON
            </button>
            <button
              className="secondary-button"
              disabled={isLocked || !scriptSegmentationResult}
              onClick={exportScriptSegmentationJson}
              type="button"
            >
              导出切分 JSON
            </button>
            <button className="secondary-button" disabled type="button">
              下载 Word（整理后可用）
            </button>
            <button
              className="primary-button"
              disabled={isLocked || !scriptSegmentationResult || scriptSegmentationResult.segments.length === 0}
              onClick={transferScriptSegmentationToStoryboard}
              type="button"
            >
              带入分镜生成
            </button>
          </div>
        </div>

        {scriptSegmentationCopyStatus && <p className="copy-status">{scriptSegmentationCopyStatus}</p>}
        {scriptSegmentationExportStatus && <p className="copy-status">{scriptSegmentationExportStatus}</p>}

        {!scriptSegmentationResult ? (
          <div className="empty-state">粘贴待改编文本并填写改编方向后，结构化结果将在这里展示。</div>
        ) : (
          <article className="script-output script-segmentation-output">
            <section className="result-summary">
              <span>项目标题</span>
              <h3>{scriptSegmentationResult.project_title}</h3>
              <p>{scriptSegmentationResult.segmentation_summary}</p>
            </section>

            <section className="image-generation-meta">
              <div>
                <span>来源类型</span>
                <strong>{formatSourceTypeLabel(String(scriptSegmentationResult.metadata?.source_type ?? ""))}</strong>
              </div>
              <div>
                <span>切分片段数</span>
                <strong>{scriptSegmentationResult.segment_count}</strong>
              </div>
              <div>
                <span>上传源标识</span>
                <strong>{scriptSegmentationResult.source_id || "-"}</strong>
              </div>
              <div>
                <span>工作区标识</span>
                <strong>{scriptSegmentationResult.workspace_id || "-"}</strong>
              </div>
              <div>
                <span>用户标识</span>
                <strong>{scriptSegmentationResult.user_id || "-"}</strong>
              </div>
              <div>
                <span>AI 功能账户</span>
                <strong>{scriptSegmentationResult.ai_account_id || "-"}</strong>
              </div>
              <div>
                <span>生成模式</span>
                <strong>{String(scriptSegmentationResult.metadata?.generation_mode ?? "-")}</strong>
              </div>
            </section>

            <section className="script-segmentation-items">
              <h4>切分片段</h4>
              <div className="script-segmentation-list">
                {scriptSegmentationResult.segments.map((segment) => (
                  <section className="script-segmentation-card" key={segment.segment_id}>
                    <div className="prompt-card-header">
                      <span>{segment.segment_id}</span>
                      <h5>{segment.title}</h5>
                    </div>

                    <dl className="prompt-detail-grid">
                      <div>
                        <dt>片段类型</dt>
                        <dd>{segment.segment_type}</dd>
                      </div>
                      <div>
                        <dt>集 / 场</dt>
                        <dd>
                          {segment.episode_number ?? "-"} / {segment.scene_number ?? "-"}
                        </dd>
                      </div>
                      <div>
                        <dt>角色</dt>
                        <dd>{segment.characters.length ? segment.characters.join("、") : "-"}</dd>
                      </div>
                      <div>
                        <dt>地点</dt>
                        <dd>{segment.location || "-"}</dd>
                      </div>
                      <div>
                        <dt>时间</dt>
                        <dd>{segment.time_of_day || "-"}</dd>
                      </div>
                      <div>
                        <dt>预计时长</dt>
                        <dd>{segment.estimated_duration_seconds ?? "-"} 秒</dd>
                      </div>
                    </dl>

                    <div className="prompt-text-block">
                      <span>摘要</span>
                      <p>{segment.summary}</p>
                    </div>

                    <div className="prompt-text-block">
                      <span>原始文本</span>
                      <p>{segment.original_text}</p>
                    </div>

                    <div className="prompt-text-block">
                      <span>冲突</span>
                      <p>{segment.conflict || "-"}</p>
                    </div>

                    <div className="prompt-text-block">
                      <span>情绪</span>
                      <p>{segment.emotion || "-"}</p>
                    </div>

                    <div className="prompt-text-block">
                      <span>视觉备注</span>
                      <p>{segment.visual_notes || "-"}</p>
                    </div>

                    <div className="prompt-text-block">
                      <span>对白文本</span>
                      <p>{segment.dialogue_text || "-"}</p>
                    </div>

                    <div className="prompt-text-block">
                      <span>下一步提示</span>
                      <p>{segment.next_step_hint || "-"}</p>
                    </div>
                  </section>
                ))}
              </div>
            </section>
          </article>
        )}
      </section>
    </section>
  );
}
