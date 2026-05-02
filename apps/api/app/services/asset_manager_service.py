from app.schemas.asset import AssetCollection, AssetItem
from app.schemas.image_generation import ImageGenerationItem, ImageGenerationOutput


MOCK_ASSET_NOTE = "Generated from ImageGenerationOutput mock result."


def build_asset_item_from_image_generation_item(
    project_title: str,
    item: ImageGenerationItem,
) -> AssetItem:
    return AssetItem(
        asset_id=f"asset-{item.task_id}",
        asset_type="image",
        project_title=project_title,
        prompt_id=item.prompt_id,
        shot_id=item.shot_id,
        task_id=item.task_id,
        provider=item.provider,
        status="available" if item.status == "succeeded" else item.status,
        url=item.image_url,
        mock_url=item.mock_url,
        local_path=item.local_path,
        width=item.width,
        height=item.height,
        seed=item.seed,
        metadata={
            **item.metadata,
            "source_task_status": item.status,
            "workflow_name": item.workflow_name,
        },
        notes=MOCK_ASSET_NOTE,
    )


def build_asset_collection_from_image_generation(output: ImageGenerationOutput) -> AssetCollection:
    assets = [
        build_asset_item_from_image_generation_item(output.project_title, item)
        for item in output.items
    ]

    return AssetCollection(
        project_title=output.project_title,
        assets=assets,
        metadata={
            "source": "image_generation",
            "provider": output.provider,
            "item_count": len(output.items),
        },
    )
