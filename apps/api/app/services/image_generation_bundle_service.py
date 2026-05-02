from app.schemas.image_generation import ImageGenerationOutput
from app.schemas.image_generation_bundle import ImageGenerationBundleOutput
from app.services.asset_manager_service import build_asset_collection_from_image_generation
from app.services.render_task_service import build_render_tasks_from_image_generation


def build_image_generation_bundle(output: ImageGenerationOutput) -> ImageGenerationBundleOutput:
    assets = build_asset_collection_from_image_generation(output)
    tasks = build_render_tasks_from_image_generation(output)

    return ImageGenerationBundleOutput(
        project_title=output.project_title,
        image_generation=output,
        assets=assets,
        tasks=tasks,
        metadata={
            "source": "image_generation_bundle",
            "provider": output.provider,
            "bundle_version": "v1",
            "image_item_count": len(output.items),
            "asset_count": len(assets.assets),
            "task_count": len(tasks.tasks),
        },
    )
