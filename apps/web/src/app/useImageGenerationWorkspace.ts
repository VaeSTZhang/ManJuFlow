import { FormEvent, useState } from "react";
import { generateImageBundle, generateImages } from "../api/imageGenerations";
import type { ToastType } from "../components/layout/Toast";
import type { ImagePromptGenerationPayload } from "./useImagePromptWorkspace";
import type {
  ImageGenerationInput,
  ImageGenerationOutput,
  ImageGenerationPromptItem,
} from "../types/imageGeneration";
import type { ImageGenerationBundleOutput } from "../types/imageGenerationBundle";

type PushToast = (type: ToastType, title: string, description?: string) => void;

type UseImageGenerationWorkspaceParams = {
  pushToast: PushToast;
  onOpenImageGenerationWorkspace: () => void;
};

const defaultImageGenerationPromptItems: ImageGenerationPromptItem[] = [
  {
    prompt_id: "P001",
    shot_id: "S001_SH001",
    positive_prompt:
      "cinematic realistic rain night hospital entrance, two characters facing each other, cold headlights",
    negative_prompt: "low quality, blurry, distorted hands, watermark",
    style_preset: "cinematic realistic",
    aspect_ratio: "9:16",
  },
];

const defaultImageGenerationForm: ImageGenerationInput = {
  project_title: "测试短剧：雨夜重逢",
  prompt_items: defaultImageGenerationPromptItems,
  provider: "mock",
  workflow_name: "system_image_generation_v1",
  aspect_ratio: "9:16",
  style_preset: "cinematic realistic",
  output_count: 1,
  seed: null,
};

function formatPromptItemsJson(items: ImageGenerationPromptItem[]): string {
  return JSON.stringify(items, null, 2);
}

export function useImageGenerationWorkspace({
  pushToast,
  onOpenImageGenerationWorkspace,
}: UseImageGenerationWorkspaceParams) {
  const [imageGenerationForm, setImageGenerationForm] =
    useState<ImageGenerationInput>(defaultImageGenerationForm);
  const [imageGenerationPromptItemsText, setImageGenerationPromptItemsText] = useState(
    formatPromptItemsJson(defaultImageGenerationPromptItems),
  );
  const [imageGenerationLoading, setImageGenerationLoading] = useState(false);
  const [imageGenerationError, setImageGenerationError] = useState("");
  const [imageGenerationResult, setImageGenerationResult] = useState<ImageGenerationOutput | null>(null);
  const [imageGenerationBundleLoading, setImageGenerationBundleLoading] = useState(false);
  const [imageGenerationBundleError, setImageGenerationBundleError] = useState("");
  const [imageGenerationBundleResult, setImageGenerationBundleResult] =
    useState<ImageGenerationBundleOutput | null>(null);

  const updateImageGenerationField = <K extends keyof ImageGenerationInput>(
    field: K,
    value: ImageGenerationInput[K],
  ) => {
    setImageGenerationForm((current) => ({ ...current, [field]: value }));
    setImageGenerationError("");
    setImageGenerationBundleError("");
  };

  const updateImageGenerationPromptItemsText = (value: string) => {
    setImageGenerationPromptItemsText(value);
    setImageGenerationError("");
    setImageGenerationBundleError("");
  };

  const applyImagePromptPayloadToGeneration = ({
    projectTitle,
    promptItems,
    aspectRatio,
    stylePreset,
  }: ImagePromptGenerationPayload): ImageGenerationInput => {
    const nextForm = {
      ...imageGenerationForm,
      project_title: projectTitle || imageGenerationForm.project_title,
      prompt_items: promptItems,
      aspect_ratio: aspectRatio || imageGenerationForm.aspect_ratio,
      style_preset: stylePreset || imageGenerationForm.style_preset,
    };

    setImageGenerationForm(nextForm);
    setImageGenerationPromptItemsText(formatPromptItemsJson(promptItems));
    setImageGenerationError("");
    setImageGenerationBundleError("");
    onOpenImageGenerationWorkspace();

    return nextForm;
  };

  const buildImageGenerationRequest = (
    promptItems: ImageGenerationPromptItem[],
    formData: ImageGenerationInput = imageGenerationForm,
    setRequestError: (message: string) => void = setImageGenerationError,
  ): ImageGenerationInput | null => {
    const projectTitle = formData.project_title.trim();

    if (!projectTitle) {
      setRequestError("请先填写项目标题。");
      pushToast("warning", "缺少必填项", "图片生成前请先填写项目标题。");
      return null;
    }

    if (promptItems.length === 0) {
      setRequestError("请至少提供 1 条 prompt_items。");
      pushToast("warning", "缺少必填项", "图片生成至少需要 1 条 prompt_items。");
      return null;
    }

    const outputCount = Number(formData.output_count) || 1;

    if (outputCount < 1 || outputCount > 4) {
      setRequestError("output_count 需要在 1 到 4 之间。");
      pushToast("warning", "参数不合法", "output_count 需要在 1 到 4 之间。");
      return null;
    }

    return {
      ...formData,
      project_title: projectTitle,
      prompt_items: promptItems,
      provider: formData.provider?.trim() || "mock",
      workflow_name: formData.workflow_name?.trim() || "system_image_generation_v1",
      aspect_ratio: formData.aspect_ratio || "9:16",
      style_preset: formData.style_preset?.trim() || "cinematic realistic",
      output_count: outputCount,
      seed: formData.seed ?? null,
    };
  };

  const parseImageGenerationPromptItems = (
    setRequestError: (message: string) => void,
  ): ImageGenerationPromptItem[] | null => {
    try {
      const parsed = JSON.parse(imageGenerationPromptItemsText) as unknown;

      if (!Array.isArray(parsed)) {
        setRequestError("prompt_items JSON 必须是数组。");
        pushToast("error", "JSON 格式错误", "prompt_items 必须是合法 JSON 数组。");
        return null;
      }

      return parsed as ImageGenerationPromptItem[];
    } catch {
      setRequestError("prompt_items JSON 解析失败，请检查格式。");
      pushToast("error", "JSON 格式错误", "prompt_items JSON 解析失败，请检查格式。");
      return null;
    }
  };

  const requestImageGeneration = async (input: ImageGenerationInput) => {
    setImageGenerationLoading(true);
    setImageGenerationError("");

    try {
      const data = await generateImages(input);
      setImageGenerationResult(data);
    } catch {
      setImageGenerationError("生成图片失败，请确认服务已启动。");
      pushToast("error", "生成失败", "图片生成请求失败，请检查服务是否运行。");
    } finally {
      setImageGenerationLoading(false);
    }
  };

  const requestImageGenerationBundle = async (input: ImageGenerationInput) => {
    setImageGenerationBundleLoading(true);
    setImageGenerationBundleError("");

    try {
      const data = await generateImageBundle(input);
      setImageGenerationBundleResult(data);
    } catch {
      setImageGenerationBundleError("生成结果包失败，请确认服务已启动。");
      pushToast("error", "结果包生成失败", "图片生成结果包请求失败，请检查服务是否运行。");
    } finally {
      setImageGenerationBundleLoading(false);
    }
  };

  const handleImageGenerationSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const promptItems = parseImageGenerationPromptItems(setImageGenerationError);

    if (!promptItems) {
      return;
    }

    const input = buildImageGenerationRequest(promptItems);

    if (!input) {
      return;
    }

    await requestImageGeneration(input);
  };

  const handleGenerateImageBundleFromManualInput = async () => {
    const promptItems = parseImageGenerationPromptItems(setImageGenerationBundleError);

    if (!promptItems) {
      return;
    }

    const input = buildImageGenerationRequest(
      promptItems,
      imageGenerationForm,
      setImageGenerationBundleError,
    );

    if (!input) {
      return;
    }

    await requestImageGenerationBundle(input);
  };

  const handleMissingImagePromptForTransfer = () => {
    setImageGenerationError("当前没有可用的绘图 Prompt 结果。");
    pushToast("warning", "缺少绘图 Prompt", "当前没有可用的绘图 Prompt 结果，无法带入图片生成。");
  };

  const generateImagesFromImagePromptPayload = async (promptPayload: ImagePromptGenerationPayload | null) => {
    if (!promptPayload) {
      setImageGenerationError("当前没有可用的绘图 Prompt 结果。");
      pushToast("warning", "缺少绘图 Prompt", "当前没有可用的绘图 Prompt 结果，无法生成图片。");
      return;
    }

    const nextForm = applyImagePromptPayloadToGeneration(promptPayload);
    pushToast("success", "已切换到图片生成", "绘图 Prompt 已带入图片生成工作区。");

    const input = buildImageGenerationRequest(promptPayload.promptItems, nextForm);

    if (!input) {
      return;
    }

    await requestImageGeneration(input);
  };

  const generateImageBundleFromImagePromptPayload = async (promptPayload: ImagePromptGenerationPayload | null) => {
    if (!promptPayload) {
      setImageGenerationBundleError("当前没有可用的绘图 Prompt 结果。");
      pushToast("warning", "缺少绘图 Prompt", "当前没有可用的绘图 Prompt 结果，无法生成结果包。");
      return;
    }

    const nextForm = applyImagePromptPayloadToGeneration(promptPayload);
    pushToast("success", "已切换到图片生成", "绘图 Prompt 已带入结果包生成流程。");

    const input = buildImageGenerationRequest(
      promptPayload.promptItems,
      nextForm,
      setImageGenerationBundleError,
    );

    if (!input) {
      return;
    }

    await requestImageGenerationBundle(input);
  };

  return {
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
  };
}
