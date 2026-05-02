import type { AssetCollection } from "./asset";
import type { ImageGenerationOutput } from "./imageGeneration";
import type { RenderTaskOutput } from "./renderTask";

export type ImageGenerationBundleOutput = {
  project_title: string;
  image_generation: ImageGenerationOutput;
  assets: AssetCollection;
  tasks: RenderTaskOutput;
  metadata?: Record<string, unknown>;
};
