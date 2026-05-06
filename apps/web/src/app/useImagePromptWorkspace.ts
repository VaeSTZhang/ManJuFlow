import { FormEvent, useState } from "react";
import { generateImagePrompts } from "../api/imagePrompts";
import type { ToastType } from "../components/layout/Toast";
import type { ImageGenerationPromptItem } from "../types/imageGeneration";
import type { ImagePromptInput, ImagePromptOutput } from "../types/imagePrompt";

type PushToast = (type: ToastType, title: string, description?: string) => void;

type ImagePromptModelOption = {
  value: string;
  label: string;
  provider?: string;
  model?: string;
};

type StoryboardPromptPayload = {
  projectTitle: string;
  storyboardSummary: string;
  storyboardText: string;
};

export type ImagePromptGenerationPayload = {
  projectTitle: string;
  promptItems: ImageGenerationPromptItem[];
  aspectRatio?: string;
  stylePreset?: string;
};

type UseImagePromptWorkspaceParams = {
  pushToast: PushToast;
  onOpenImagePromptWorkspace: () => void;
  onImagePromptReadyForGeneration: (payload: ImagePromptGenerationPayload) => void;
  onMissingImagePromptForGeneration: () => void;
};

const defaultImagePromptForm: ImagePromptInput = {
  project_title: "测试短剧：雨夜重逢",
  storyboard_summary: "医院门口雨夜重逢，男女主在冷色车灯和雨幕中对峙。",
  storyboard_text:
    "第1场｜医院门口｜雨夜。镜头1：林晚撑着黑伞站在医院门口台阶边，雨水打湿地面。镜头2：顾沉从黑色轿车里下来，两人在车灯和雨幕中对视。",
  target_model: "general",
  aspect_ratio: "9:16",
  style_preset: "cinematic realistic",
  language: "en",
  extra_requirements: "保持雨夜、冷色光影、电影感写实风格。",
};

const imagePromptModelOptions: ImagePromptModelOption[] = [
  { value: "default", label: "系统默认模型" },
  { value: "deepseek", label: "DeepSeek / deepseek-chat", provider: "deepseek", model: "deepseek-chat" },
  { value: "mimo", label: "Mimo / mimo-v2.5-pro", provider: "mimo", model: "mimo-v2.5-pro" },
  { value: "kimi", label: "Kimi / kimi-k2.5", provider: "kimi", model: "kimi-k2.5" },
  { value: "minimax", label: "MiniMax / MiniMax-M2.7", provider: "minimax", model: "MiniMax-M2.7" },
];

function sanitizeFileName(value: string): string {
  return value
    .trim()
    .replace(/[\\/:*?"<>|]/g, "-")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60);
}

export function useImagePromptWorkspace({
  pushToast,
  onOpenImagePromptWorkspace,
  onImagePromptReadyForGeneration,
  onMissingImagePromptForGeneration,
}: UseImagePromptWorkspaceParams) {
  const [imagePromptForm, setImagePromptForm] = useState<ImagePromptInput>(defaultImagePromptForm);
  const [imagePromptResult, setImagePromptResult] = useState<ImagePromptOutput | null>(null);
  const [imagePromptLoading, setImagePromptLoading] = useState(false);
  const [imagePromptError, setImagePromptError] = useState("");
  const [imagePromptTransferStatus, setImagePromptTransferStatus] = useState("");
  const [imagePromptCopyStatus, setImagePromptCopyStatus] = useState("");
  const [imagePromptExportStatus, setImagePromptExportStatus] = useState("");

  const selectedImagePromptModel =
    imagePromptModelOptions.find((option) => option.provider === imagePromptForm.llm_provider) ||
    imagePromptModelOptions[0];

  const updateImagePromptField = <K extends keyof ImagePromptInput>(field: K, value: ImagePromptInput[K]) => {
    setImagePromptForm((current) => ({ ...current, [field]: value }));
    setImagePromptTransferStatus("");
    setImagePromptCopyStatus("");
    setImagePromptExportStatus("");
  };

  const updateImagePromptModel = (value: string) => {
    const option = imagePromptModelOptions.find((item) => item.value === value) || imagePromptModelOptions[0];

    setImagePromptForm((current) => ({
      ...current,
      llm_provider: option.provider,
      llm_model: option.model,
    }));
    setImagePromptTransferStatus("");
    setImagePromptCopyStatus("");
    setImagePromptExportStatus("");
  };

  const setImagePromptFromStoryboard = ({
    projectTitle,
    storyboardSummary,
    storyboardText,
  }: StoryboardPromptPayload) => {
    setImagePromptForm((current) => ({
      ...current,
      project_title: projectTitle,
      storyboard_summary: storyboardSummary,
      storyboard_text: storyboardText,
    }));
    setImagePromptTransferStatus("已将分镜结果带入绘图 Prompt 输入区。");
    setImagePromptError("");
    setImagePromptCopyStatus("");
    setImagePromptExportStatus("");
    onOpenImagePromptWorkspace();
    pushToast("success", "已切换到绘图 Prompt", "分镜结果已带入绘图 Prompt 工作区。");
  };

  const handleImagePromptSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!imagePromptForm.project_title.trim()) {
      setImagePromptError("请先填写项目标题。");
      pushToast("warning", "缺少必填项", "生成绘图 Prompt 前请先填写项目标题。");
      return;
    }

    if (!imagePromptForm.storyboard_text?.trim()) {
      setImagePromptError("请先填写分镜文本。");
      pushToast("warning", "缺少必填项", "生成绘图 Prompt 前请先填写分镜文本。");
      return;
    }

    setImagePromptLoading(true);
    setImagePromptError("");
    setImagePromptTransferStatus("");
    setImagePromptCopyStatus("");
    setImagePromptExportStatus("");

    try {
      const selectedProvider = imagePromptForm.llm_provider?.trim();
      const selectedModel = imagePromptForm.llm_model?.trim();
      const data = await generateImagePrompts({
        ...imagePromptForm,
        project_title: imagePromptForm.project_title.trim(),
        storyboard_summary: imagePromptForm.storyboard_summary?.trim() || null,
        storyboard_text: imagePromptForm.storyboard_text.trim(),
        target_model: imagePromptForm.target_model || "general",
        aspect_ratio: imagePromptForm.aspect_ratio || "9:16",
        style_preset: imagePromptForm.style_preset || "cinematic realistic",
        language: imagePromptForm.language || "en",
        llm_provider: selectedProvider || undefined,
        llm_model: selectedModel || undefined,
      });
      setImagePromptResult(data);
    } catch {
      setImagePromptError("生成绘图 Prompt 失败，请确认服务已启动。");
      pushToast("error", "生成失败", "分镜转绘图 Prompt 请求失败，请检查服务是否运行。");
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
      pushToast("success", "复制成功", "绘图 Prompt JSON 已复制到剪贴板。");
    } catch {
      setImagePromptError("复制绘图 Prompt JSON 失败，请检查浏览器剪贴板权限。");
      pushToast("error", "复制失败", "复制绘图 Prompt JSON 失败，请检查浏览器剪贴板权限。");
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
    pushToast("success", "导出成功", "绘图 Prompt JSON 已导出。");
  };

  const getImagePromptGenerationPayload = (): ImagePromptGenerationPayload | null => {
    if (!imagePromptResult?.items.length) {
      return null;
    }

    const promptItems = imagePromptResult.items.map(
      (item): ImageGenerationPromptItem => ({
        prompt_id: item.prompt_id,
        shot_id: item.shot_id,
        positive_prompt: item.positive_prompt,
        negative_prompt: item.negative_prompt,
        style_preset: item.style_preset,
        aspect_ratio: item.aspect_ratio,
        model_hint: item.model_hint,
        seed: item.seed,
        metadata: {
          scene_id: item.scene_id,
          shot_number: item.shot_number,
          scene_number: item.scene_number,
        },
      }),
    );

    return {
      projectTitle: imagePromptResult.project_title,
      promptItems,
      aspectRatio: imagePromptResult.aspect_ratio,
      stylePreset: imagePromptResult.style_preset,
    };
  };

  const transferImagePromptToImageGeneration = () => {
    const payload = getImagePromptGenerationPayload();

    if (!payload) {
      onMissingImagePromptForGeneration();
      return;
    }

    onImagePromptReadyForGeneration(payload);
    pushToast("success", "已切换到图片生成", "绘图 Prompt 已带入图片生成工作区。");
  };

  return {
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
  };
}
