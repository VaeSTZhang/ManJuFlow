import type { SelectedCreativeModel } from "../ai/CreativeModelPanel";
import type { ShortDramaGenerationInput } from "../../types/scriptGeneration";

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

function buildCreativeModelMetadata(selectedModel: SelectedCreativeModel): Record<string, unknown> {
  // metadata.creative_model is transitional: step 217 should replace this with
  // AIRequestOptions or another explicit request-level model override contract.
  return {
    provider: selectedModel.provider,
    model: selectedModel.model,
    label: selectedModel.label,
    source: selectedModel.source,
  };
}

export function buildIdeaGenerationInput(
  draft: IdeaGenerationDraftInput,
  selectedModel: SelectedCreativeModel,
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
    metadata: {
      source_entry: "idea",
      creative_model: buildCreativeModelMetadata(selectedModel),
    },
  };
}

export function buildFilmScriptGenerationInput(
  draft: AdaptationGenerationDraftInput,
  selectedModel: SelectedCreativeModel,
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
    metadata: {
      source_entry: "film_script",
      source_title: trimToOptional(draft.sourceTitle),
      creative_model: buildCreativeModelMetadata(selectedModel),
    },
  };
}

export function buildNovelGenerationInput(
  draft: AdaptationGenerationDraftInput,
  selectedModel: SelectedCreativeModel,
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
    metadata: {
      source_entry: "novel",
      source_title: trimToOptional(draft.sourceTitle),
      creative_model: buildCreativeModelMetadata(selectedModel),
    },
  };
}
