import { FormEvent, useEffect, useState } from "react";
import { generateImageBundle, generateImages } from "./api/imageGenerations";
import { generateImagePrompts } from "./api/imagePrompts";
import { generateStoryboard } from "./api/storyboards";
import "./App.css";
import { AppShell } from "./components/layout/AppShell";
import { Sidebar } from "./components/layout/Sidebar";
import { Toast } from "./components/layout/Toast";
import {
  ScriptSegmentationWorkspace,
  type ScriptSegmentationStoryboardPayload,
} from "./components/workspaces/ScriptSegmentationWorkspace";
import type {
  ImageGenerationInput,
  ImageGenerationOutput,
  ImageGenerationPromptItem,
} from "./types/imageGeneration";
import type { ImageGenerationBundleOutput } from "./types/imageGenerationBundle";
import type { ImagePromptInput, ImagePromptOutput } from "./types/imagePrompt";
import type { StoryboardInput, StoryboardOutput } from "./types/storyboard";
import type { SidebarItem } from "./components/layout/Sidebar";
import type { ToastMessage, ToastType } from "./components/layout/Toast";

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

type ImagePromptModelOption = {
  value: string;
  label: string;
  provider?: string;
  model?: string;
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
  storyboard_summary: "医院门口雨夜重逢，男女主在冷色车灯和雨幕中对峙。",
  storyboard_text:
    "第1场｜医院门口｜雨夜。镜头1：林晚撑着黑伞站在医院门口台阶边，雨水打湿地面。镜头2：顾沉从黑色轿车里下来，两人在车灯和雨幕中对视。",
  target_model: "general",
  aspect_ratio: "9:16",
  style_preset: "cinematic realistic",
  language: "en",
  extra_requirements: "保持雨夜、冷色光影、电影感写实风格。",
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
  workflow_name: "mock_image_generation_v1",
  aspect_ratio: "9:16",
  style_preset: "cinematic realistic",
  output_count: 1,
  seed: null,
};

const imagePromptModelOptions: ImagePromptModelOption[] = [
  { value: "default", label: "使用后端默认" },
  { value: "deepseek", label: "DeepSeek / deepseek-chat", provider: "deepseek", model: "deepseek-chat" },
  { value: "mimo", label: "Mimo / mimo-v2.5-pro", provider: "mimo", model: "mimo-v2.5-pro" },
  { value: "kimi", label: "Kimi / kimi-k2.5", provider: "kimi", model: "kimi-k2.5" },
  { value: "minimax", label: "MiniMax / MiniMax-M2.7", provider: "minimax", model: "MiniMax-M2.7" },
];

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

function sanitizeFileName(value: string): string {
  return value
    .trim()
    .replace(/[\\/:*?"<>|]/g, "-")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60);
}

function formatPromptItemsJson(items: ImageGenerationPromptItem[]): string {
  return JSON.stringify(items, null, 2);
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

const sidebarItems: SidebarItem[] = [
  {
    id: "idea-script",
    label: "灵感创作",
    description: "Idea → Script",
  },
  {
    id: "script-segmentation",
    label: "已有剧本",
    description: "Import → Segments",
  },
  {
    id: "storyboard",
    label: "分镜生成",
    description: "Script → Storyboard",
  },
  {
    id: "image-prompt",
    label: "绘图 Prompt",
    description: "Storyboard → Prompt",
  },
  {
    id: "image-generation",
    label: "图片生成",
    description: "ImageGeneration mock",
  },
  {
    id: "assets-tasks",
    label: "资产与任务",
    description: "Assets / Tasks",
  },
  {
    id: "system-status",
    label: "系统状态",
    description: "Runtime status",
  },
];

function App() {
  const [activeWorkspaceId, setActiveWorkspaceId] = useState("idea-script");
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
  const [toastMessages, setToastMessages] = useState<ToastMessage[]>([]);

  const selectedImagePromptModel =
    imagePromptModelOptions.find((option) => option.provider === imagePromptForm.llm_provider) ||
    imagePromptModelOptions[0];

  const dismissToast = (id: string) => {
    setToastMessages((current) => current.filter((message) => message.id !== id));
  };

  const pushToast = (type: ToastType, title: string, description?: string) => {
    const id = `${Date.now()}-${Math.random()}`;

    setToastMessages((current) => [...current, { id, type, title, description }]);
    window.setTimeout(() => dismissToast(id), 3500);
  };

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
        pushToast("warning", "后端状态未知", "系统状态接口请求失败，请确认后端服务是否已启动。");
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

  const updateImageGenerationField = <K extends keyof ImageGenerationInput>(
    field: K,
    value: ImageGenerationInput[K],
  ) => {
    setImageGenerationForm((current) => ({ ...current, [field]: value }));
    setImageGenerationError("");
    setImageGenerationBundleError("");
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
      pushToast("error", "生成失败", "剧本生成接口请求失败，请检查后端是否运行。");
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
    pushToast("success", "复制成功", "结构化剧本 JSON 已复制到剪贴板。");
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
    pushToast("success", "导出成功", "结构化剧本 JSON 已导出。");
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
    setActiveWorkspaceId("storyboard");
    pushToast("success", "已切换到分镜生成", "结构化剧本已带入剧本转分镜工作区。");
  };

  const applyScriptSegmentationToStoryboard = (payload: ScriptSegmentationStoryboardPayload) => {
    setStoryboardForm((current) => ({
      ...current,
      project_title: payload.project_title,
      script_text: payload.script_text,
    }));
    setStoryboardTransferStatus("已将已有剧本切分结果带入分镜生成，请确认后点击生成分镜。");
    setStoryboardError("");
    setStoryboardCopyStatus("");
    setStoryboardExportStatus("");
    setActiveWorkspaceId("storyboard");
    pushToast("success", "已切换到分镜生成", "已有剧本切分结果已带入分镜生成，请确认后点击生成分镜。");
  };

  const transferStoryboardToImagePrompt = () => {
    if (!storyboardResult) {
      return;
    }

    setImagePromptForm((current) => ({
      ...current,
      project_title: storyboardResult.project_title,
      storyboard_summary: storyboardResult.storyboard_summary,
      storyboard_text: JSON.stringify(storyboardResult, null, 2),
    }));
    setImagePromptTransferStatus("已将分镜结果带入绘图 Prompt 输入区。");
    setImagePromptError("");
    setImagePromptCopyStatus("");
    setImagePromptExportStatus("");
    setActiveWorkspaceId("image-prompt");
    pushToast("success", "已切换到绘图 Prompt", "分镜结果已带入绘图 Prompt 工作区。");
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
      pushToast("error", "生成失败", "剧本转分镜接口请求失败，请检查后端是否运行。");
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
    pushToast("success", "复制成功", "分镜 JSON 已复制到剪贴板。");
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
    pushToast("success", "导出成功", "分镜 JSON 已导出。");
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
      setImagePromptError("生成绘图 Prompt 失败，请确认后端服务已启动：http://127.0.0.1:8000");
      pushToast("error", "生成失败", "分镜转绘图 Prompt 接口请求失败，请检查后端是否运行。");
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
      workflow_name: formData.workflow_name?.trim() || "mock_image_generation_v1",
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

  const mapImagePromptResultToImageGenerationItems = (): ImageGenerationPromptItem[] | null => {
    if (!imagePromptResult?.items.length) {
      return null;
    }

    return imagePromptResult.items.map(
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
  };

  const transferImagePromptToImageGeneration = () => {
    const promptItems = mapImagePromptResultToImageGenerationItems();

    if (!promptItems) {
      setImageGenerationError("当前没有可用的绘图 Prompt 结果。");
      pushToast("warning", "缺少绘图 Prompt", "当前没有可用的绘图 Prompt 结果，无法带入图片生成。");
      return;
    }

    const nextForm = {
      ...imageGenerationForm,
      project_title: imagePromptResult?.project_title || imageGenerationForm.project_title,
      prompt_items: promptItems,
      aspect_ratio: imagePromptResult?.aspect_ratio || imageGenerationForm.aspect_ratio,
      style_preset: imagePromptResult?.style_preset || imageGenerationForm.style_preset,
    };

    setImageGenerationForm(nextForm);
    setImageGenerationPromptItemsText(formatPromptItemsJson(promptItems));
    setImageGenerationError("");
    setImageGenerationBundleError("");
    setActiveWorkspaceId("image-generation");
    pushToast("success", "已切换到图片生成", "绘图 Prompt 已带入 Image Generation 工作区。");
  };

  const requestImageGeneration = async (input: ImageGenerationInput) => {
    setImageGenerationLoading(true);
    setImageGenerationError("");

    try {
      const data = await generateImages(input);
      setImageGenerationResult(data);
    } catch {
      setImageGenerationError("生成 mock 图片失败，请确认后端服务已启动：http://127.0.0.1:8000");
      pushToast("error", "生成失败", "图片生成接口请求失败，请检查后端是否运行。");
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
      setImageGenerationBundleError("生成 Bundle 失败，请确认后端服务已启动：http://127.0.0.1:8000");
      pushToast("error", "Bundle 生成失败", "generate-bundle 接口请求失败，请检查后端是否运行。");
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

  const generateImagesFromImagePromptResult = async () => {
    if (!imagePromptResult?.items.length) {
      setImageGenerationError("当前没有可用的绘图 Prompt 结果。");
      pushToast("warning", "缺少绘图 Prompt", "当前没有可用的绘图 Prompt 结果，无法生成 mock 图片。");
      return;
    }

    const promptItems = mapImagePromptResultToImageGenerationItems();

    if (!promptItems) {
      return;
    }

    const nextForm = {
      ...imageGenerationForm,
      project_title: imagePromptResult.project_title,
      prompt_items: promptItems,
      aspect_ratio: imagePromptResult.aspect_ratio,
      style_preset: imagePromptResult.style_preset,
    };

    setImageGenerationForm(nextForm);
    setImageGenerationPromptItemsText(formatPromptItemsJson(promptItems));
    setActiveWorkspaceId("image-generation");
    pushToast("success", "已切换到图片生成", "绘图 Prompt 已带入图片生成工作区。");

    const input = buildImageGenerationRequest(promptItems, nextForm);

    if (!input) {
      return;
    }

    await requestImageGeneration(input);
  };

  const generateImageBundleFromImagePromptResult = async () => {
    const promptItems = mapImagePromptResultToImageGenerationItems();

    if (!promptItems) {
      setImageGenerationBundleError("当前没有可用的绘图 Prompt 结果。");
      pushToast("warning", "缺少绘图 Prompt", "当前没有可用的绘图 Prompt 结果，无法生成 Bundle。");
      return;
    }

    const nextForm = {
      ...imageGenerationForm,
      project_title: imagePromptResult?.project_title || imageGenerationForm.project_title,
      prompt_items: promptItems,
      aspect_ratio: imagePromptResult?.aspect_ratio || imageGenerationForm.aspect_ratio,
      style_preset: imagePromptResult?.style_preset || imageGenerationForm.style_preset,
    };

    setImageGenerationForm(nextForm);
    setImageGenerationPromptItemsText(formatPromptItemsJson(promptItems));
    setActiveWorkspaceId("image-generation");
    pushToast("success", "已切换到图片生成", "绘图 Prompt 已带入 Bundle 生成流程。");

    const input = buildImageGenerationRequest(
      promptItems,
      nextForm,
      setImageGenerationBundleError,
    );

    if (!input) {
      return;
    }

    await requestImageGenerationBundle(input);
  };

  const formatTaskProgress = (progress?: number | null): string => {
    if (typeof progress !== "number") {
      return "-";
    }

    return `${Math.round(progress * 100)}%`;
  };

  const activeWorkspace = sidebarItems.find((item) => item.id === activeWorkspaceId) || sidebarItems[0];

  const renderAssetTaskDetails = () => {
    if (!imageGenerationBundleResult) {
      return (
        <div className="empty-state workspace-empty">
          暂无资产与任务，请先在 Image Generation 中生成 Bundle。
        </div>
      );
    }

    return (
      <section className="image-generation-bundle-summary">
        <div className="result-summary">
          <span>Bundle 项目</span>
          <h3>{imageGenerationBundleResult.project_title || "未设置"}</h3>
        </div>

        <section className="image-generation-meta">
          <div>
            <span>Image Items</span>
            <strong>{imageGenerationBundleResult.image_generation?.items?.length ?? 0}</strong>
          </div>
          <div>
            <span>Assets</span>
            <strong>{imageGenerationBundleResult.assets?.assets?.length ?? 0}</strong>
          </div>
          <div>
            <span>Tasks</span>
            <strong>{imageGenerationBundleResult.tasks?.tasks?.length ?? 0}</strong>
          </div>
          <div>
            <span>Metadata Source</span>
            <strong>{String(imageGenerationBundleResult.metadata?.source ?? "未设置")}</strong>
          </div>
        </section>

        <section className="bundle-detail-section">
          <h4>Assets 明细</h4>
          {imageGenerationBundleResult.assets?.assets?.length ? (
            <div className="bundle-detail-list">
              {imageGenerationBundleResult.assets.assets.map((asset) => (
                <article className="bundle-detail-card asset-card" key={asset.asset_id}>
                  <div className="mock-image-placeholder compact-placeholder">
                    <strong>Mock Image Asset</strong>
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
                      <dt>Asset Type</dt>
                      <dd>{asset.asset_type || "-"}</dd>
                    </div>
                    <div>
                      <dt>Provider</dt>
                      <dd>{asset.provider || "-"}</dd>
                    </div>
                    <div>
                      <dt>Prompt ID</dt>
                      <dd>{asset.prompt_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>Shot ID</dt>
                      <dd>{asset.shot_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>Task ID</dt>
                      <dd>{asset.task_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>Mock URL</dt>
                      <dd className="code-text">{asset.mock_url || "-"}</dd>
                    </div>
                    <div>
                      <dt>Local Path</dt>
                      <dd className="code-text">{asset.local_path || "-"}</dd>
                    </div>
                    <div>
                      <dt>尺寸</dt>
                      <dd>
                        {asset.width ?? "?"} x {asset.height ?? "?"}
                      </dd>
                    </div>
                    <div>
                      <dt>Seed</dt>
                      <dd>{asset.seed ?? "-"}</dd>
                    </div>
                    <div>
                      <dt>Metadata Source</dt>
                      <dd>{String(asset.metadata?.source ?? "-")}</dd>
                    </div>
                  </dl>

                  {asset.notes && (
                    <div className="bundle-note">
                      <span>Notes</span>
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
          <h4>Tasks 明细</h4>
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
                      <dt>Task Type</dt>
                      <dd>{task.task_type || "-"}</dd>
                    </div>
                    <div>
                      <dt>Progress</dt>
                      <dd className="progress-text">{formatTaskProgress(task.progress)}</dd>
                    </div>
                    <div>
                      <dt>Provider</dt>
                      <dd>{task.provider || "-"}</dd>
                    </div>
                    <div>
                      <dt>Workflow</dt>
                      <dd>{task.workflow_name || "-"}</dd>
                    </div>
                    <div>
                      <dt>Prompt ID</dt>
                      <dd>{task.prompt_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>Shot ID</dt>
                      <dd>{task.shot_id || "-"}</dd>
                    </div>
                    <div>
                      <dt>Asset IDs</dt>
                      <dd className="code-text">{task.asset_ids?.length ? task.asset_ids.join(", ") : "-"}</dd>
                    </div>
                    <div>
                      <dt>Error Code</dt>
                      <dd>{task.error_code || "-"}</dd>
                    </div>
                    <div>
                      <dt>Error Message</dt>
                      <dd>{task.error_message || "-"}</dd>
                    </div>
                    <div>
                      <dt>Metadata Source</dt>
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
          onSelect={setActiveWorkspaceId}
        />
      }
      toast={<Toast messages={toastMessages} onDismiss={dismissToast} />}
      topbar={
        <div className="workspace-topbar-content">
          <div>
            <span>当前工作区</span>
            <strong>{activeWorkspace.label}</strong>
          </div>
          <p>当前工作区仅显示对应操作区域。</p>
        </div>
      }
    >
      <main className="app">
      <div className="workspace-transition" key={activeWorkspaceId}>
      {activeWorkspaceId === "idea-script" && (
        <>
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
        </>
      )}

      {activeWorkspaceId === "storyboard" && (
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
          onApplyToStoryboard={applyScriptSegmentationToStoryboard}
          onNotify={pushToast}
        />
      )}

      {activeWorkspaceId === "image-prompt" && (
      <section className="image-prompt-workspace" id="image-prompt-workspace">
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

          <div className="model-selection-note">
            <strong>
              当前模型：
              {selectedImagePromptModel.provider
                ? ` ${selectedImagePromptModel.label}`
                : " 使用后端默认"}
            </strong>
            <p>模型选择仅在后端 IMAGE_PROMPT_GENERATION_MODE=llm 时生效。mock 模式下不会消耗 API 额度。</p>
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
      )}

      {activeWorkspaceId === "image-generation" && (
      <section className="image-generation-workspace">
        <form className="panel form-panel" onSubmit={handleImageGenerationSubmit}>
          <div className="panel-heading">
            <p>第四阶段</p>
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
              <span>Provider</span>
              <select
                value={imageGenerationForm.provider || "mock"}
                onChange={(event) => updateImageGenerationField("provider", event.target.value)}
              >
                <option value="mock">mock</option>
              </select>
            </label>

            <label className="field">
              <span>Workflow</span>
              <input
                value={imageGenerationForm.workflow_name || "mock_image_generation_v1"}
                onChange={(event) => updateImageGenerationField("workflow_name", event.target.value)}
              />
            </label>

            <label className="field">
              <span>画面比例</span>
              <select
                value={imageGenerationForm.aspect_ratio || "9:16"}
                onChange={(event) => updateImageGenerationField("aspect_ratio", event.target.value)}
              >
                <option value="9:16">9:16</option>
                <option value="16:9">16:9</option>
                <option value="1:1">1:1</option>
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
              <span>Seed</span>
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
              onChange={(event) => {
                setImageGenerationPromptItemsText(event.target.value);
                setImageGenerationError("");
                setImageGenerationBundleError("");
              }}
              rows={9}
            />
          </label>

          <button
            className="secondary-button"
            disabled={!imagePromptResult?.items.length || imageGenerationLoading}
            onClick={generateImagesFromImagePromptResult}
            type="button"
          >
            使用绘图 Prompt 结果生成 mock 图片
          </button>

          <button
            className="secondary-button"
            disabled={!imagePromptResult?.items.length || imageGenerationBundleLoading}
            onClick={generateImageBundleFromImagePromptResult}
            type="button"
          >
            使用绘图 Prompt 结果生成 Bundle
          </button>

          <button
            className="secondary-button"
            disabled={imageGenerationBundleLoading}
            onClick={handleGenerateImageBundleFromManualInput}
            type="button"
          >
            {imageGenerationBundleLoading ? "生成 Bundle 中..." : "生成 Bundle（图片 + 资产 + 任务）"}
          </button>

          <button className="primary-button" disabled={imageGenerationLoading} type="submit">
            {imageGenerationLoading ? "生成中..." : "生成 mock 图片"}
          </button>

          {imageGenerationError && <p className="error-message">{imageGenerationError}</p>}
          {imageGenerationBundleError && <p className="error-message">{imageGenerationBundleError}</p>}
        </form>

        <section className="panel result-panel">
          <div className="result-header">
            <div>
              <p>输出预览</p>
              <h2>Image Generation</h2>
            </div>
          </div>

          {imageGenerationBundleResult && (
            <section className="image-generation-bundle-summary">
              <div className="result-summary">
                <span>Bundle 项目</span>
                <h3>{imageGenerationBundleResult.project_title || "未设置"}</h3>
              </div>

              <section className="image-generation-meta">
                <div>
                  <span>Image Items</span>
                  <strong>{imageGenerationBundleResult.image_generation?.items?.length ?? 0}</strong>
                </div>
                <div>
                  <span>Assets</span>
                  <strong>{imageGenerationBundleResult.assets?.assets?.length ?? 0}</strong>
                </div>
                <div>
                  <span>Tasks</span>
                  <strong>{imageGenerationBundleResult.tasks?.tasks?.length ?? 0}</strong>
                </div>
                <div>
                  <span>Metadata Source</span>
                  <strong>{String(imageGenerationBundleResult.metadata?.source ?? "未设置")}</strong>
                </div>
                <div>
                  <span>Provider</span>
                  <strong>{String(imageGenerationBundleResult.metadata?.provider ?? "未设置")}</strong>
                </div>
                <div>
                  <span>Bundle Version</span>
                  <strong>{String(imageGenerationBundleResult.metadata?.bundle_version ?? "未设置")}</strong>
                </div>
              </section>

              <section className="bundle-detail-section">
                <h4>Assets 明细</h4>
                {imageGenerationBundleResult.assets?.assets?.length ? (
                  <div className="bundle-detail-list">
                    {imageGenerationBundleResult.assets.assets.map((asset) => (
                      <article className="bundle-detail-card asset-card" key={asset.asset_id}>
                        <div className="mock-image-placeholder compact-placeholder">
                          <strong>Mock Image Asset</strong>
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
                            <dt>Asset Type</dt>
                            <dd>{asset.asset_type || "-"}</dd>
                          </div>
                          <div>
                            <dt>Provider</dt>
                            <dd>{asset.provider || "-"}</dd>
                          </div>
                          <div>
                            <dt>Prompt ID</dt>
                            <dd>{asset.prompt_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>Shot ID</dt>
                            <dd>{asset.shot_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>Task ID</dt>
                            <dd>{asset.task_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>尺寸</dt>
                            <dd>
                              {asset.width ?? "?"} x {asset.height ?? "?"}
                            </dd>
                          </div>
                          <div>
                            <dt>Seed</dt>
                            <dd>{asset.seed ?? "-"}</dd>
                          </div>
                          <div>
                            <dt>Metadata Source</dt>
                            <dd>{String(asset.metadata?.source ?? "-")}</dd>
                          </div>
                          <div>
                            <dt>Mock URL</dt>
                            <dd className="code-text">{asset.mock_url || "-"}</dd>
                          </div>
                          <div>
                            <dt>Local Path</dt>
                            <dd className="code-text">{asset.local_path || "-"}</dd>
                          </div>
                        </dl>

                        {asset.notes && (
                          <div className="bundle-note">
                            <span>Notes</span>
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
                <h4>Tasks 明细</h4>
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
                            <dt>Task Type</dt>
                            <dd>{task.task_type || "-"}</dd>
                          </div>
                          <div>
                            <dt>Progress</dt>
                            <dd className="progress-text">{formatTaskProgress(task.progress)}</dd>
                          </div>
                          <div>
                            <dt>Provider</dt>
                            <dd>{task.provider || "-"}</dd>
                          </div>
                          <div>
                            <dt>Workflow</dt>
                            <dd>{task.workflow_name || "-"}</dd>
                          </div>
                          <div>
                            <dt>Prompt ID</dt>
                            <dd>{task.prompt_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>Shot ID</dt>
                            <dd>{task.shot_id || "-"}</dd>
                          </div>
                          <div>
                            <dt>Asset IDs</dt>
                            <dd className="code-text">{task.asset_ids?.length ? task.asset_ids.join(", ") : "-"}</dd>
                          </div>
                          <div>
                            <dt>Error Code</dt>
                            <dd>{task.error_code || "-"}</dd>
                          </div>
                          <div>
                            <dt>Metadata Source</dt>
                            <dd>{String(task.metadata?.source ?? "-")}</dd>
                          </div>
                        </dl>

                        {(task.status === "failed" || task.error_message) && (
                          <div className="bundle-note task-error-note">
                            <span>Error Message</span>
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
            <div className="empty-state">生成图片 mock 结果将在这里展示。</div>
          ) : (
            <article className="script-output image-generation-output">
              <section className="result-summary">
                <span>项目标题</span>
                <h3>{imageGenerationResult.project_title}</h3>
              </section>

              <section className="image-generation-meta">
                <div>
                  <span>Provider</span>
                  <strong>{imageGenerationResult.provider}</strong>
                </div>
                <div>
                  <span>Status</span>
                  <strong>{imageGenerationResult.status}</strong>
                </div>
                <div>
                  <span>Items</span>
                  <strong>{imageGenerationResult.items.length}</strong>
                </div>
              </section>

              <section className="image-generation-items">
                <h4>Mock 图片结果</h4>
                <div className="image-generation-list">
                  {imageGenerationResult.items.map((item) => (
                    <section className="image-generation-card" key={item.task_id}>
                      <div className="mock-image-placeholder">
                        <strong>Mock Image</strong>
                        <span>{item.mock_url || "无 mock_url"}</span>
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
                          <dt>Prompt ID</dt>
                          <dd>{item.prompt_id}</dd>
                        </div>
                        <div>
                          <dt>Shot ID</dt>
                          <dd>{item.shot_id}</dd>
                        </div>
                        <div>
                          <dt>Mock URL</dt>
                          <dd>{item.mock_url || "未设置"}</dd>
                        </div>
                        <div>
                          <dt>Local Path</dt>
                          <dd>{item.local_path || "未设置"}</dd>
                        </div>
                        <div>
                          <dt>尺寸</dt>
                          <dd>
                            {item.width ?? "?"} x {item.height ?? "?"}
                          </dd>
                        </div>
                        <div>
                          <dt>Seed</dt>
                          <dd>{item.seed ?? "未设置"}</dd>
                        </div>
                        <div>
                          <dt>Metadata Source</dt>
                          <dd>{String(item.metadata?.source ?? "未设置")}</dd>
                        </div>
                      </dl>

                      <div className="prompt-text-block positive-prompt">
                        <span>Positive Prompt</span>
                        <p>{item.positive_prompt}</p>
                      </div>

                      <div className="prompt-text-block negative-prompt">
                        <span>Negative Prompt</span>
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
            <p>第四阶段</p>
            <h2>资产与任务</h2>
          </div>
          {renderAssetTaskDetails()}
        </section>
      )}

      {activeWorkspaceId === "system-status" && (
        <section className="workspace-section">
          <div className="workspace-header">
            <p>系统状态</p>
            <h2>Runtime Status</h2>
          </div>

          <section className="panel result-panel system-status-panel">
            <div className="system-status system-status-detail" aria-label="后端系统状态">
              <div className={isSystemConnected ? "status-dot status-ok" : "status-dot status-offline"} />
              <div>
                <p>{isSystemConnected ? `后端状态：${systemStatus?.status}` : "后端状态：未连接"}</p>
                {isSystemConnected && systemStatus ? (
                  <>
                    <p>应用名称：{systemStatus.app_name}</p>
                    <p>运行环境：{systemStatus.app_env}</p>
                    <p>生成模式：{systemStatus.script_generation_mode}</p>
                    <p>LLM：{systemStatus.llm_enabled ? "已启用" : "未启用"}</p>
                  </>
                ) : (
                  <p>请确认后端服务已启动：http://127.0.0.1:8000</p>
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
