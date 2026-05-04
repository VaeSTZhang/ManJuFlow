import { useState } from "react";
import type {
  AdaptationDraft,
  AdaptationMode,
  CreationDrafts,
  IdeaCreationDraft,
} from "../../components/creation/creationDraftTypes";

const defaultIdeaDraft: IdeaCreationDraft = {
  projectTitle: "",
  ideaText: "",
  genreStyle: "悬疑短剧 / 强钩子、快节奏",
  episodeCount: 10,
  extraRequirements: "",
};

const defaultAdaptationDraft: AdaptationDraft = {
  projectTitle: "",
  sourceTitle: "",
  sourceText: "",
  focus: "",
  episodeCount: 10,
  extraRequirements: "",
};

const defaultCreationDrafts: CreationDrafts = {
  idea: { ...defaultIdeaDraft },
  film: { ...defaultAdaptationDraft },
  novel: { ...defaultAdaptationDraft },
};

export function useCreationDrafts() {
  const [drafts, setDrafts] = useState<CreationDrafts>(defaultCreationDrafts);

  const updateIdeaDraft = <K extends keyof IdeaCreationDraft>(
    field: K,
    value: IdeaCreationDraft[K],
  ) => {
    setDrafts((current) => ({
      ...current,
      idea: {
        ...current.idea,
        [field]: value,
      },
    }));
  };

  const updateAdaptationDraft = <K extends keyof AdaptationDraft>(
    mode: AdaptationMode,
    field: K,
    value: AdaptationDraft[K],
  ) => {
    setDrafts((current) => ({
      ...current,
      [mode]: {
        ...current[mode],
        [field]: value,
      },
    }));
  };

  return {
    drafts,
    updateIdeaDraft,
    updateAdaptationDraft,
  };
}
