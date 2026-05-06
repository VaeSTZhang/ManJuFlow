import type { SelectedCreativeModel } from "../ai/CreativeModelPanel";
import type { AdaptationMode, CreationDrafts } from "./creationDraftTypes";
import type { AIRequestPurpose, ShortDramaGenerationInput } from "../../types/scriptGeneration";
import type { BuildContextOptions } from "../../utils/contextOptions";

export type IdeaGenerationDraftInput = {
  projectTitle: string;
  ideaText: string;
  genreStyle: string;
  episodeCount: number;
  extraRequirements: string;
};

export type AdaptationGenerationDraftInput = {
  projectTitle: string;
  sourceTitle: string;
  sourceText: string;
  focus: string;
  episodeCount: number;
  extraRequirements: string;
};

type ShortDramaGenerationRequestMode = "idea" | AdaptationMode;

type BuildShortDramaGenerationRequestParams = {
  mode: ShortDramaGenerationRequestMode;
  drafts: CreationDrafts;
  selectedModel: SelectedCreativeModel;
  buildContextOptions: BuildContextOptions;
};

type ShortDramaGenerationRequest = {
  requestInput: ShortDramaGenerationInput;
  sourceLabel: string;
};

function trimToOptional(value: string): string | null {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

function resolveEpisodeCount(value: number): number {
  if (!Number.isFinite(value)) {
    return 10;
  }

  const normalized = Math.round(value);
  return normalized > 0 ? normalized : 10;
}

function buildAIRequestOptions(
  selectedModel: SelectedCreativeModel,
  purpose: AIRequestPurpose,
): ShortDramaGenerationInput["ai_options"] {
  const useSystemDefault = selectedModel.source === "system_default";

  return {
    provider: useSystemDefault ? undefined : selectedModel.provider,
    model: useSystemDefault ? undefined : selectedModel.model,
    language: "zh",
    purpose,
  };
}

export function buildIdeaGenerationInput(
  draft: IdeaGenerationDraftInput,
  selectedModel: SelectedCreativeModel,
  buildContextOptions: BuildContextOptions,
): ShortDramaGenerationInput {
  const genreStyle = trimToOptional(draft.genreStyle) ?? "短剧";

  return {
    project_title: trimToOptional(draft.projectTitle) ?? "未命名灵感短剧",
    source_mode: "idea",
    idea_text: trimToOptional(draft.ideaText),
    target_episode_count: resolveEpisodeCount(draft.episodeCount),
    genre: genreStyle,
    style: genreStyle,
    extra_requirements: trimToOptional(draft.extraRequirements),
    language: "zh",
    ai_options: buildAIRequestOptions(selectedModel, "script_generation"),
    context_options: buildContextOptions("generated_script"),
    metadata: {
      source_entry: "idea",
    },
  };
}

export function buildFilmScriptGenerationInput(
  draft: AdaptationGenerationDraftInput,
  selectedModel: SelectedCreativeModel,
  buildContextOptions: BuildContextOptions,
): ShortDramaGenerationInput {
  return {
    project_title: trimToOptional(draft.projectTitle) ?? "未命名电影改编短剧",
    source_mode: "film_script",
    source_text: trimToOptional(draft.sourceText),
    target_episode_count: resolveEpisodeCount(draft.episodeCount),
    genre: "电影剧本改编",
    style: trimToOptional(draft.focus) ?? "强钩子、快节奏、适合短剧",
    adaptation_goal: trimToOptional(draft.focus),
    extra_requirements: trimToOptional(draft.extraRequirements),
    language: "zh",
    ai_options: buildAIRequestOptions(selectedModel, "film_adaptation"),
    context_options: buildContextOptions("generated_script"),
    metadata: {
      source_entry: "film_script",
      source_title: trimToOptional(draft.sourceTitle),
    },
  };
}

export function buildNovelGenerationInput(
  draft: AdaptationGenerationDraftInput,
  selectedModel: SelectedCreativeModel,
  buildContextOptions: BuildContextOptions,
): ShortDramaGenerationInput {
  return {
    project_title: trimToOptional(draft.projectTitle) ?? "未命名小说改编短剧",
    source_mode: "novel",
    source_text: trimToOptional(draft.sourceText),
    target_episode_count: resolveEpisodeCount(draft.episodeCount),
    genre: "小说 / 网文改编",
    style: trimToOptional(draft.focus) ?? "强钩子、快节奏、适合短剧",
    adaptation_goal: trimToOptional(draft.focus),
    extra_requirements: trimToOptional(draft.extraRequirements),
    language: "zh",
    ai_options: buildAIRequestOptions(selectedModel, "novel_adaptation"),
    context_options: buildContextOptions("generated_script"),
    metadata: {
      source_entry: "novel",
      source_title: trimToOptional(draft.sourceTitle),
    },
  };
}

export function buildShortDramaGenerationRequest({
  mode,
  drafts,
  selectedModel,
  buildContextOptions,
}: BuildShortDramaGenerationRequestParams): ShortDramaGenerationRequest {
  if (mode === "idea") {
    return {
      requestInput: buildIdeaGenerationInput(drafts.idea, selectedModel, buildContextOptions),
      sourceLabel: "灵感生成",
    };
  }

  if (mode === "film") {
    return {
      requestInput: buildFilmScriptGenerationInput(drafts.film, selectedModel, buildContextOptions),
      sourceLabel: "电影剧本改编",
    };
  }

  return {
    requestInput: buildNovelGenerationInput(drafts.novel, selectedModel, buildContextOptions),
    sourceLabel: "小说 / 网文改编",
  };
}
