import type { ScriptSourceMode } from "../types/scriptGeneration";

export type CreationEntryStatus = "available" | "planned" | "mock";

export type CreationEntryConfig = {
  id: string;
  sourceMode: ScriptSourceMode;
  label: string;
  subtitle: string;
  description: string;
  inputLabel: string;
  placeholder: string;
  maxInputChars: number;
  defaultGenre: string;
  defaultStyle: string;
  defaultEpisodeCount: number;
  status: CreationEntryStatus;
  primaryActionLabel: string;
  nextStepLabel: string;
};

export const CREATION_ENTRY_REGISTRY: CreationEntryConfig[] = [
  {
    id: "idea",
    sourceMode: "idea",
    label: "灵感生成短剧",
    subtitle: "从一句创意开始",
    description: "输入故事灵感、人物关系或爽点方向，生成结构化短剧剧本。",
    inputLabel: "灵感内容",
    placeholder:
      "例：雨夜里，一位年轻编剧收到母亲留下的旧剧本，剧本里的每一场戏都在现实中逐渐发生。",
    maxInputChars: 5000,
    defaultGenre: "悬疑短剧",
    defaultStyle: "强钩子、快节奏、适合短剧",
    defaultEpisodeCount: 4,
    status: "available",
    primaryActionLabel: "生成短剧剧本",
    nextStepLabel: "生成后可在线编辑、导出，并进入下一大功能",
  },
  {
    id: "film_script",
    sourceMode: "film_script",
    label: "电影剧本改短剧",
    subtitle: "长剧本短剧化",
    description: "将电影剧本、长剧本或分场文本改编成短剧节奏。",
    inputLabel: "电影剧本 / 长剧本文本",
    placeholder:
      "例：废弃片场内，女主回到父亲未完成的最后一场戏。制片人阻止她开机，却被旧摄影机自动亮起的红灯打断。",
    maxInputChars: 100000,
    defaultGenre: "悬疑短剧",
    defaultStyle: "强钩子、快节奏、低成本可拍摄",
    defaultEpisodeCount: 8,
    status: "mock",
    primaryActionLabel: "改编为短剧剧本",
    nextStepLabel: "生成后可在线编辑、下载 DOCX，并进入 Prompt 工作流",
  },
  {
    id: "novel",
    sourceMode: "novel",
    label: "小说改短剧",
    subtitle: "叙事文本场景化",
    description: "将小说、网文或故事文本改编成可拍、可演、可分镜的短剧剧本。",
    inputLabel: "小说 / 网文 / 故事文本",
    placeholder:
      "例：旧书店即将拆除，女主在夹层里发现母亲的日记。日记最后一页写着：不要相信剧场里的掌声。",
    maxInputChars: 100000,
    defaultGenre: "悬疑短剧",
    defaultStyle: "人物关系强、情绪推进快、适合短剧",
    defaultEpisodeCount: 8,
    status: "mock",
    primaryActionLabel: "改编为短剧剧本",
    nextStepLabel: "生成后可在线编辑、下载 DOCX，并进入 Prompt 工作流",
  },
];

export function getCreationEntryBySourceMode(
  sourceMode: ScriptSourceMode,
): CreationEntryConfig | undefined {
  return CREATION_ENTRY_REGISTRY.find((entry) => entry.sourceMode === sourceMode);
}

export function getAvailableCreationEntries(): CreationEntryConfig[] {
  return CREATION_ENTRY_REGISTRY.filter((entry) => entry.status === "available");
}
