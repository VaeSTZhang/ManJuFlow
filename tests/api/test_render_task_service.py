from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.image_generation import ImageGenerationItem, ImageGenerationOutput
from app.schemas.render_task import RenderTaskOutput
from app.services.render_task_service import build_render_tasks_from_image_generation


def make_image_generation_item(**overrides) -> ImageGenerationItem:
    data = {
        "task_id": "mock-img-P001-1",
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "status": "succeeded",
        "positive_prompt": "cinematic realistic rain night hospital entrance",
        "negative_prompt": "low quality, blurry, watermark",
        "provider": "mock",
        "workflow_name": "mock_image_generation_v1",
        "mock_url": "/mock/images/mock-img-P001-1.png",
        "local_path": "mock_outputs/images/mock-img-P001-1.png",
        "width": 1080,
        "height": 1920,
        "seed": 101,
        "metadata": {"source": "mock"},
    }
    data.update(overrides)
    return ImageGenerationItem(**data)


def make_image_generation_output(**overrides) -> ImageGenerationOutput:
    data = {
        "project_title": "测试短剧：雨夜重逢",
        "provider": "mock",
        "status": "succeeded",
        "items": [make_image_generation_item()],
        "metadata": {"source": "mock"},
    }
    data.update(overrides)
    return ImageGenerationOutput(**data)


def test_build_render_tasks_from_image_generation_returns_output_schema() -> None:
    result = build_render_tasks_from_image_generation(make_image_generation_output())

    assert isinstance(result, RenderTaskOutput)


def test_build_render_tasks_keeps_project_title() -> None:
    output = make_image_generation_output()

    result = build_render_tasks_from_image_generation(output)

    assert result.project_title == output.project_title


def test_build_render_tasks_count_matches_generation_items() -> None:
    output = make_image_generation_output(
        items=[
            make_image_generation_item(task_id="mock-img-P001-1", prompt_id="P001", shot_id="S001_SH001"),
            make_image_generation_item(task_id="mock-img-P002-1", prompt_id="P002", shot_id="S001_SH002"),
        ]
    )

    result = build_render_tasks_from_image_generation(output)

    assert len(result.tasks) == 2


def test_build_render_tasks_maps_task_prompt_and_shot_ids() -> None:
    result = build_render_tasks_from_image_generation(make_image_generation_output())
    task = result.tasks[0]

    assert task.task_id == "mock-img-P001-1"
    assert task.prompt_id == "P001"
    assert task.shot_id == "S001_SH001"


def test_succeeded_item_progress_is_one() -> None:
    result = build_render_tasks_from_image_generation(make_image_generation_output())

    assert result.tasks[0].progress == 1.0


def test_succeeded_item_asset_ids_include_asset_task_id() -> None:
    result = build_render_tasks_from_image_generation(make_image_generation_output())

    assert result.tasks[0].asset_ids == ["asset-mock-img-P001-1"]


def test_running_item_progress_is_half() -> None:
    result = build_render_tasks_from_image_generation(
        make_image_generation_output(items=[make_image_generation_item(status="running")])
    )

    assert result.tasks[0].progress == 0.5


def test_pending_item_progress_is_zero() -> None:
    result = build_render_tasks_from_image_generation(
        make_image_generation_output(items=[make_image_generation_item(status="pending")])
    )

    assert result.tasks[0].progress == 0.0


def test_failed_item_progress_is_one() -> None:
    result = build_render_tasks_from_image_generation(
        make_image_generation_output(items=[make_image_generation_item(status="failed")])
    )

    assert result.tasks[0].progress == 1.0


def test_failed_item_has_generation_failed_error_code() -> None:
    result = build_render_tasks_from_image_generation(
        make_image_generation_output(items=[make_image_generation_item(status="failed")])
    )

    assert result.tasks[0].error_code == "generation_failed"


def test_failed_item_maps_error_message() -> None:
    result = build_render_tasks_from_image_generation(
        make_image_generation_output(
            items=[make_image_generation_item(status="failed", error_message="mock failure")]
        )
    )

    assert result.tasks[0].error_message == "mock failure"


def test_build_render_tasks_metadata_contains_source_provider_and_count() -> None:
    result = build_render_tasks_from_image_generation(make_image_generation_output())

    assert result.metadata["source"] == "image_generation"
    assert result.metadata["provider"] == "mock"
    assert result.metadata["task_count"] == 1


def test_build_render_task_item_metadata_contains_source_and_asset_flag() -> None:
    result = build_render_tasks_from_image_generation(make_image_generation_output())

    assert result.tasks[0].metadata["source"] == "image_generation"
    assert result.tasks[0].metadata["workflow_name"] == "mock_image_generation_v1"
    assert result.tasks[0].metadata["has_asset"] is True


def test_build_render_tasks_does_not_access_real_queue_or_external_services() -> None:
    result = build_render_tasks_from_image_generation(make_image_generation_output())
    task = result.tasks[0]

    assert task.provider == "mock"
    assert task.workflow_name == "mock_image_generation_v1"
    assert task.asset_ids == ["asset-mock-img-P001-1"]
