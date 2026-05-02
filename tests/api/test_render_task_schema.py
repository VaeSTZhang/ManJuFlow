from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.render_task import RenderTaskItem, RenderTaskOutput


def make_render_task_item(**overrides) -> RenderTaskItem:
    data = {
        "task_id": "TASK_001",
        "project_title": "测试短剧：雨夜重逢",
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "workflow_name": "mock_image_generation_v1",
        "progress": 1,
        "asset_ids": ["ASSET_001"],
    }
    data.update(overrides)
    return RenderTaskItem(**data)


def test_render_task_item_can_be_created() -> None:
    task = make_render_task_item()

    assert task.task_id == "TASK_001"
    assert task.project_title == "测试短剧：雨夜重逢"


def test_render_task_item_defaults_task_type_to_image_generation() -> None:
    task = RenderTaskItem(task_id="TASK_001")

    assert task.task_type == "image_generation"


def test_render_task_item_defaults_provider_to_mock() -> None:
    task = RenderTaskItem(task_id="TASK_001")

    assert task.provider == "mock"


def test_render_task_item_defaults_status_to_succeeded() -> None:
    task = RenderTaskItem(task_id="TASK_001")

    assert task.status == "succeeded"


@pytest.mark.parametrize("progress", [0, 0.5, 1])
def test_render_task_item_accepts_progress_between_zero_and_one(progress: float) -> None:
    task = make_render_task_item(progress=progress)

    assert task.progress == progress


def test_render_task_item_rejects_progress_less_than_zero() -> None:
    with pytest.raises(ValidationError):
        make_render_task_item(progress=-0.1)


def test_render_task_item_rejects_progress_greater_than_one() -> None:
    with pytest.raises(ValidationError):
        make_render_task_item(progress=1.1)


def test_render_task_output_can_include_multiple_tasks() -> None:
    output = RenderTaskOutput(
        project_title="测试短剧：雨夜重逢",
        tasks=[
            make_render_task_item(task_id="TASK_001"),
            make_render_task_item(task_id="TASK_002", prompt_id="P002", shot_id="S001_SH002"),
        ],
    )

    assert len(output.tasks) == 2


def test_render_task_output_model_dump_contains_project_title_and_tasks() -> None:
    output = RenderTaskOutput(project_title="测试短剧：雨夜重逢", tasks=[make_render_task_item()])

    data = output.model_dump()

    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert len(data["tasks"]) == 1


def test_render_task_item_rejects_empty_task_id() -> None:
    with pytest.raises(ValidationError):
        RenderTaskItem(task_id="")
