import { FormEvent, useState } from "react";
import { createApiErrorFromResponse, parseApiErrorMessage } from "../api/errors";
import type { ToastType } from "../components/layout/Toast";

type PushToast = (type: ToastType, title: string, description?: string) => void;

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

type TransferScriptToStoryboardPayload = {
  projectTitle: string;
  scriptText: string;
};

type UseLegacyIdeaScriptWorkspaceParams = {
  isBrowsingMode: boolean;
  pushToast: PushToast;
  requireLogin: () => void;
  onTransferScriptToStoryboard: (payload: TransferScriptToStoryboardPayload) => void;
  onClearStoryboardTransferStatus: () => void;
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

const IDEA_TEXT_MAX_CHARS = 5_000;

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

export function useLegacyIdeaScriptWorkspace({
  isBrowsingMode,
  pushToast,
  requireLogin,
  onTransferScriptToStoryboard,
  onClearStoryboardTransferStatus,
}: UseLegacyIdeaScriptWorkspaceParams) {
  const [form, setForm] = useState<IdeaInput>(defaultForm);
  const [result, setResult] = useState<ScriptOutput | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [copyStatus, setCopyStatus] = useState("");
  const [exportStatus, setExportStatus] = useState("");
  const isIdeaTextTooLong = form.idea_text.length > IDEA_TEXT_MAX_CHARS;

  const updateField = <K extends keyof IdeaInput>(field: K, value: IdeaInput[K]) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (isBrowsingMode) {
      requireLogin();
      return;
    }

    if (isIdeaTextTooLong) {
      setError("灵感内容已超出 5,000 字，请删减后再生成。");
      pushToast("warning", "灵感内容过长", "灵感内容已超出 5,000 字，请删减后再生成。");
      return;
    }

    setIsLoading(true);
    setError("");
    setCopyStatus("");
    setExportStatus("");
    onClearStoryboardTransferStatus();

    try {
      const response = await fetch("http://127.0.0.1:8000/api/scripts/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw await createApiErrorFromResponse(response, "生成剧本失败，请确认服务已启动。");
      }

      const data = (await response.json()) as ScriptOutput;
      setResult(data);
    } catch (error) {
      const message = parseApiErrorMessage(error, "生成剧本失败，请确认服务已启动。");
      setError(message);
      pushToast("error", "生成失败", message);
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
    link.download = "dramora-script-output.json";
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

    onTransferScriptToStoryboard({
      projectTitle: result.project_title,
      scriptText: formatScriptForStoryboard(result),
    });
  };

  return {
    form,
    result,
    isLoading,
    error,
    copyStatus,
    exportStatus,
    isIdeaTextTooLong,
    ideaTextMaxChars: IDEA_TEXT_MAX_CHARS,
    updateField,
    handleSubmit,
    copyJson,
    exportJson,
    transferScriptToStoryboard,
  };
}
