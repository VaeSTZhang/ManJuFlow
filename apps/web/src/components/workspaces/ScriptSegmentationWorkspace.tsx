import { FormEvent, useState } from "react";
import { segmentScript } from "../../api/scriptSegmentation";
import { uploadScriptMock } from "../../api/uploads";
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
  onApplyToStoryboard: (payload: ScriptSegmentationStoryboardPayload) => void;
  onNotify?: (type: NotificationType, title: string, description?: string) => void;
};

const maxScriptTextChars = 100_000;

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
    "已有剧本切分片段：",
    segmentsText,
  ].join("\n");
}

export function ScriptSegmentationWorkspace({
  initialProjectTitle,
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

  const scriptSegmentationTextLength = scriptSegmentationForm.script_text?.length || 0;
  const isScriptSegmentationTextTooLong = scriptSegmentationTextLength > maxScriptTextChars;

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

    if (!scriptSegmentationForm.project_title.trim()) {
      setScriptSegmentationError("请先填写项目标题。");
      notify("warning", "缺少必填项", "切分已有剧本前请先填写项目标题。");
      return;
    }

    if (!scriptSegmentationForm.script_text?.trim() && !scriptSegmentationForm.source_id?.trim()) {
      setScriptSegmentationError("请先粘贴已有剧本文本。");
      notify("warning", "缺少剧本文本", "请粘贴已有剧本文本后再执行切分。");
      return;
    }

    if (isScriptSegmentationTextTooLong) {
      setScriptSegmentationError("当前文本超过 100,000 字符，请拆分后再切分。");
      notify("warning", "文本过长", "当前文本超过 100,000 字符，请拆分后再切分。");
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
      notify("success", "切分完成", "已有剧本已生成 mock 结构化片段。");
    } catch {
      setScriptSegmentationError("切分已有剧本失败，请确认后端服务已启动：http://127.0.0.1:8000");
      notify("error", "切分失败", "已有剧本切分接口请求失败，请检查后端是否运行。");
    } finally {
      setScriptSegmentationLoading(false);
    }
  };

  const handleMockScriptUpload = async () => {
    if (!scriptSegmentationForm.project_title.trim()) {
      setScriptUploadError("请先填写项目标题。");
      notify("warning", "缺少必填项", "模拟上传 Word 文档前请先填写项目标题。");
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
      notify("success", "上传 mock 完成", "已将提取文本填入下方剧本文本框，可继续切分。");
    } catch {
      setScriptUploadError("模拟上传 Word 文档失败，请确认后端服务已启动：http://127.0.0.1:8000");
      notify("error", "上传失败", "上传 Word 文档 mock 接口请求失败，请检查后端是否运行。");
    } finally {
      setScriptUploadLoading(false);
    }
  };

  const copyScriptSegmentationJson = async () => {
    if (!scriptSegmentationResult) {
      return;
    }

    try {
      await navigator.clipboard.writeText(JSON.stringify(scriptSegmentationResult, null, 2));
      setScriptSegmentationCopyStatus("已复制切分 JSON");
      setScriptSegmentationExportStatus("");
      setScriptSegmentationError("");
      notify("success", "复制成功", "已有剧本切分 JSON 已复制到剪贴板。");
    } catch {
      setScriptSegmentationError("复制切分 JSON 失败，请检查浏览器剪贴板权限。");
      notify("error", "复制失败", "复制已有剧本切分 JSON 失败，请检查浏览器剪贴板权限。");
    }
  };

  const exportScriptSegmentationJson = () => {
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
    notify("success", "导出成功", "已有剧本切分 JSON 已导出。");
  };

  const transferScriptSegmentationToStoryboard = () => {
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
          <p>第五阶段</p>
          <h2>已有剧本导入与切分</h2>
          <span>支持粘贴已有剧本文本，或通过 mock 上传 Word 文档提取文本。切分后可继续进入分镜生成。</span>
        </div>

        <label className="field field-wide">
          <span>项目标题</span>
          <input
            value={scriptSegmentationForm.project_title}
            onChange={(event) => updateScriptSegmentationField("project_title", event.target.value)}
          />
        </label>

        <section className="script-upload-mock-card">
          <div>
            <h3>上传 Word 剧本文档（模拟）</h3>
            <p>当前为模拟上传流程，暂不读取真实文件；真实 .docx 上传将在后续小闭环接入。</p>
          </div>

          <button
            className="secondary-button"
            disabled={scriptUploadLoading}
            onClick={handleMockScriptUpload}
            type="button"
          >
            {scriptUploadLoading ? "模拟上传中..." : "模拟上传 Word 文档"}
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
              <p>已将提取文本填入下方剧本文本框，可继续切分。</p>
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
          <span>已有剧本文本</span>
          <textarea
            value={scriptSegmentationForm.script_text || ""}
            onChange={(event) => updateScriptSegmentationField("script_text", event.target.value)}
            rows={10}
          />
        </label>

        <div className="script-text-counter">
          <span className={isScriptSegmentationTextTooLong ? "text-limit-exceeded" : ""}>
            当前字符数：{scriptSegmentationTextLength} / {maxScriptTextChars}
          </span>
          {scriptSegmentationForm.source_id && <span>上传源标识：{scriptSegmentationForm.source_id}</span>}
        </div>

        {isScriptSegmentationTextTooLong && (
          <p className="error-message">当前文本超过 100,000 字符，请拆分后再切分。</p>
        )}

        <div className="field-grid">
          <label className="field">
            <span>来源类型</span>
            <input
              value={scriptSegmentationForm.source_type || "pasted_text"}
              onChange={(event) => updateScriptSegmentationField("source_type", event.target.value)}
            />
          </label>

          <label className="field">
            <span>切分粒度</span>
            <select
              value={scriptSegmentationForm.target_segment_level || "scene"}
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
              onChange={(event) => updateScriptSegmentationField("language", event.target.value)}
            >
              <option value="zh">中文</option>
              <option value="en">英文</option>
            </select>
          </label>
        </div>

        <label className="field field-wide">
          <span>额外要求</span>
          <textarea
            value={scriptSegmentationForm.extra_requirements || ""}
            onChange={(event) => updateScriptSegmentationField("extra_requirements", event.target.value)}
            rows={3}
          />
        </label>

        <button
          className="primary-button"
          disabled={scriptSegmentationLoading || isScriptSegmentationTextTooLong}
          type="submit"
        >
          {scriptSegmentationLoading ? "切分中..." : "切分已有剧本"}
        </button>

        {scriptSegmentationError && <p className="error-message">{scriptSegmentationError}</p>}
      </form>

      <section className="panel result-panel">
        <div className="result-header">
          <div>
            <p>输出预览</p>
            <h2>剧本切分结果</h2>
          </div>
          <div className="result-actions">
            <button
              className="secondary-button"
              disabled={!scriptSegmentationResult}
              onClick={copyScriptSegmentationJson}
              type="button"
            >
              复制切分 JSON
            </button>
            <button
              className="secondary-button"
              disabled={!scriptSegmentationResult}
              onClick={exportScriptSegmentationJson}
              type="button"
            >
              导出切分 JSON
            </button>
            <button
              className="primary-button"
              disabled={!scriptSegmentationResult || scriptSegmentationResult.segments.length === 0}
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
          <div className="empty-state">粘贴已有剧本或模拟上传 Word 文档后，切分结果将在这里展示。</div>
        ) : (
          <article className="script-output script-segmentation-output">
            <section className="result-summary">
              <span>项目标题</span>
              <h3>{scriptSegmentationResult.project_title}</h3>
              <p>{scriptSegmentationResult.segmentation_summary}</p>
            </section>

            <section className="image-generation-meta">
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
