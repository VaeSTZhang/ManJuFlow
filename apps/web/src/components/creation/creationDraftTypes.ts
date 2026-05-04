import type { DocumentImportAdaptationMode } from "../../hooks/creation/useDocumentImportDrafts";

export type CreationMode = "idea" | "adaptation";
export type AdaptationMode = DocumentImportAdaptationMode;

export type IdeaCreationDraft = {
  projectTitle: string;
  ideaText: string;
  genreStyle: string;
  episodeCount: number;
  extraRequirements: string;
};

export type AdaptationDraft = {
  projectTitle: string;
  sourceTitle: string;
  sourceText: string;
  focus: string;
  episodeCount: number;
  extraRequirements: string;
};

export type CreationDrafts = {
  idea: IdeaCreationDraft;
  film: AdaptationDraft;
  novel: AdaptationDraft;
};
