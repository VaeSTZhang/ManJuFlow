from app.schemas.image_generation import ImageGenerationItem, ImageGenerationOutput
from app.schemas.render_task import RenderTaskItem, RenderTaskOutput


def _get_mock_progress(status: str) -> float | None:
    if status == "succeeded":
        return 1.0

    if status == "failed":
        return 1.0

    if status == "pending":
        return 0.0

    if status == "running":
        return 0.5

    return None


def build_render_task_item_from_image_generation_item(
    project_title: str,
    item: ImageGenerationItem,
) -> RenderTaskItem:
    has_asset = item.status == "succeeded"

    return RenderTaskItem(
        task_id=item.task_id,
        task_type="image_generation",
        project_title=project_title,
        prompt_id=item.prompt_id,
        shot_id=item.shot_id,
        provider=item.provider,
        workflow_name=item.workflow_name,
        status=item.status,
        progress=_get_mock_progress(item.status),
        asset_ids=[f"asset-{item.task_id}"] if has_asset else [],
        error_code="generation_failed" if item.status == "failed" else None,
        error_message=item.error_message,
        metadata={
            "source": "image_generation",
            "workflow_name": item.workflow_name,
            "has_asset": has_asset,
        },
    )


def build_render_tasks_from_image_generation(output: ImageGenerationOutput) -> RenderTaskOutput:
    tasks = [
        build_render_task_item_from_image_generation_item(output.project_title, item)
        for item in output.items
    ]

    return RenderTaskOutput(
        project_title=output.project_title,
        tasks=tasks,
        metadata={
            "source": "image_generation",
            "provider": output.provider,
            "task_count": len(output.items),
        },
    )
