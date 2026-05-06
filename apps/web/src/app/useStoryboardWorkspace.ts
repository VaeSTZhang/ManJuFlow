import { FormEvent, useState } from "react";
import { generateStoryboard } from "../api/storyboards";
import type { ToastType } from "../components/layout/Toast";
import type { StoryboardInput, StoryboardOutput } from "../types/storyboard";

type PushToast = (type: ToastType, title: string, description?: string) => void;

type StoryboardScriptPayload = {
  projectTitle: string;
  scriptText: string;
  transferStatus: string;
  toastDescription: string;
};

type StoryboardPromptPayload = {
  projectTitle: string;
  storyboardSummary: string;
  storyboardText: string;
};

type UseStoryboardWorkspaceParams = {
  pushToast: PushToast;
  onOpenStoryboardWorkspace: () => void;
  onStoryboardReadyForPrompt: (payload: StoryboardPromptPayload) => void;
};

const defaultStoryboardForm: StoryboardInput = {
  project_title: "测试短剧：雨夜重逢",
  script_text:
    "第1集 第1场｜医院门口｜雨夜。暴雨中，林晚撑着黑伞站在医院门口，顾沉从车里下来，两人隔雨对视。顾沉：你终于肯回来了？林晚：我回来，不是为了见你。",
};

export function useStoryboardWorkspace({
  pushToast,
  onOpenStoryboardWorkspace,
  onStoryboardReadyForPrompt,
}: UseStoryboardWorkspaceParams) {
  const [storyboardForm, setStoryboardForm] = useState<StoryboardInput>(defaultStoryboardForm);
  const [storyboardResult, setStoryboardResult] = useState<StoryboardOutput | null>(null);
  const [isStoryboardLoading, setIsStoryboardLoading] = useState(false);
  const [storyboardError, setStoryboardError] = useState("");
  const [storyboardCopyStatus, setStoryboardCopyStatus] = useState("");
  const [storyboardExportStatus, setStoryboardExportStatus] = useState("");
  const [storyboardTransferStatus, setStoryboardTransferStatus] = useState("");

  const updateStoryboardField = <K extends keyof StoryboardInput>(field: K, value: StoryboardInput[K]) => {
    setStoryboardForm((current) => ({ ...current, [field]: value }));
    setStoryboardTransferStatus("");
  };

  const setStoryboardFromScript = ({
    projectTitle,
    scriptText,
    transferStatus,
    toastDescription,
  }: StoryboardScriptPayload) => {
    setStoryboardForm((current) => ({
      ...current,
      project_title: projectTitle,
      script_text: scriptText,
    }));
    setStoryboardTransferStatus(transferStatus);
    setStoryboardError("");
    setStoryboardCopyStatus("");
    setStoryboardExportStatus("");
    onOpenStoryboardWorkspace();
    pushToast("success", "已切换到分镜生成", toastDescription);
  };

  const clearStoryboardTransferStatus = () => {
    setStoryboardTransferStatus("");
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
      setStoryboardError("生成分镜失败，请确认服务已启动。");
      pushToast("error", "生成失败", "剧本转分镜请求失败，请检查服务是否运行。");
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
    link.download = "dramora-storyboard-output.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    setStoryboardExportStatus("已导出分镜 JSON");
    setStoryboardCopyStatus("");
    pushToast("success", "导出成功", "分镜 JSON 已导出。");
  };

  const transferStoryboardToImagePrompt = () => {
    if (!storyboardResult) {
      return;
    }

    onStoryboardReadyForPrompt({
      projectTitle: storyboardResult.project_title,
      storyboardSummary: storyboardResult.storyboard_summary,
      storyboardText: JSON.stringify(storyboardResult, null, 2),
    });
  };

  return {
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
  };
}
