import { useState } from "react";
import { exportDocument, exportDocumentFile } from "../../api/documentExport";
import { parseApiErrorMessage } from "../../api/errors";
import type { ShortDramaScriptOutput } from "../../types/scriptGeneration";

type UseScriptDocumentExportParams = {
  effectiveScript: ShortDramaScriptOutput | null;
  edited: boolean;
  sourceLabel?: string;
  modelLabel: string;
  generatedAt?: string;
  lastEditedAt?: string;
  onError: (message: string) => void;
  onSuccess?: () => void;
};

function downloadBlobFile(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function downloadTextFile(filename: string, content: string, mimeType: string) {
  downloadBlobFile(filename, new Blob([content], { type: mimeType }));
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

export function useScriptDocumentExport({
  effectiveScript,
  edited,
  sourceLabel,
  modelLabel,
  generatedAt,
  lastEditedAt,
  onError,
  onSuccess,
}: UseScriptDocumentExportParams) {
  const [isExportingScript, setIsExportingScript] = useState(false);

  const buildExportMetadata = () => ({
    edited,
    source_mode: effectiveScript?.source_mode ?? null,
    generated_at: generatedAt ?? null,
    last_edited_at: lastEditedAt ?? null,
    exported_from: "creation_home",
  });

  const downloadShortDramaJson = async () => {
    if (!effectiveScript || isExportingScript) {
      return;
    }

    setIsExportingScript(true);
    try {
      const output = await exportDocument({
        project_title: effectiveScript.project_title,
        document_type: "short_drama_script",
        source_stage: "script",
        structured_payload: effectiveScript as unknown as Record<string, unknown>,
        export_format: "json",
        filename: "dramora-short-drama-script.json",
        metadata: buildExportMetadata(),
      });

      downloadTextFile(
        output.filename,
        output.content_text ?? "",
        "application/json;charset=utf-8",
      );
      onSuccess?.();
    } catch (error) {
      onError(parseApiErrorMessage(error, "导出失败，请稍后重试或联系技术支持。"));
    } finally {
      setIsExportingScript(false);
    }
  };

  const downloadShortDramaTxt = async () => {
    if (!effectiveScript || isExportingScript) {
      return;
    }

    const contentText = formatShortDramaScriptTxt(
      effectiveScript,
      sourceLabel ?? "系统默认",
      modelLabel,
      generatedAt ?? "生成后显示",
    );

    setIsExportingScript(true);
    try {
      const output = await exportDocument({
        project_title: effectiveScript.project_title,
        document_type: "short_drama_script",
        source_stage: "script",
        content_text: contentText,
        structured_payload: effectiveScript as unknown as Record<string, unknown>,
        export_format: "txt",
        filename: "dramora-short-drama-script.txt",
        metadata: buildExportMetadata(),
      });

      downloadTextFile(
        output.filename,
        output.content_text ?? contentText,
        "text/plain;charset=utf-8",
      );
      onSuccess?.();
    } catch (error) {
      onError(parseApiErrorMessage(error, "导出失败，请稍后重试或联系技术支持。"));
    } finally {
      setIsExportingScript(false);
    }
  };

  const downloadShortDramaDocx = async () => {
    if (!effectiveScript || isExportingScript) {
      return;
    }

    setIsExportingScript(true);
    try {
      const output = await exportDocumentFile({
        project_title: effectiveScript.project_title,
        document_type: "short_drama_script",
        source_stage: "script",
        structured_payload: effectiveScript as unknown as Record<string, unknown>,
        export_format: "docx",
        filename: "dramora-short-drama-script.docx",
        metadata: buildExportMetadata(),
      });

      downloadBlobFile(
        output.filename,
        output.blob.type ? output.blob : new Blob([output.blob], { type: output.contentType }),
      );
      onSuccess?.();
    } catch (error) {
      onError(parseApiErrorMessage(error, "导出失败，请稍后重试或联系技术支持。"));
    } finally {
      setIsExportingScript(false);
    }
  };

  return {
    downloadShortDramaDocx,
    downloadShortDramaJson,
    downloadShortDramaTxt,
    isExportingScript,
  };
}
