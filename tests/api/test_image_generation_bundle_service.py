from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.image_generation import ImageGenerationItem, ImageGenerationOutput
from app.schemas.image_generation_bundle import ImageGenerationBundleOutput
from app.services.image_generation_bundle_service import build_image_generation_bundle


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
        "items": [
            make_image_generation_item(task_id="mock-img-P001-1", prompt_id="P001", shot_id="S001_SH001"),
            make_image_generation_item(task_id="mock-img-P002-1", prompt_id="P002", shot_id="S001_SH002"),
        ],
        "metadata": {"source": "mock"},
    }
    data.update(overrides)
    return ImageGenerationOutput(**data)


def test_build_image_generation_bundle_returns_bundle_output() -> None:
    result = build_image_generation_bundle(make_image_generation_output())

    assert isinstance(result, ImageGenerationBundleOutput)


def test_build_image_generation_bundle_keeps_project_title() -> None:
    output = make_image_generation_output()

    result = build_image_generation_bundle(output)

    assert result.project_title == output.project_title


def test_build_image_generation_bundle_keeps_original_image_generation_output() -> None:
    output = make_image_generation_output()

    result = build_image_generation_bundle(output)

    assert result.image_generation == output


def test_build_image_generation_bundle_asset_count_matches_image_items() -> None:
    output = make_image_generation_output()

    result = build_image_generation_bundle(output)

    assert len(result.assets.assets) == len(output.items)


def test_build_image_generation_bundle_task_count_matches_image_items() -> None:
    output = make_image_generation_output()

    result = build_image_generation_bundle(output)

    assert len(result.tasks.tasks) == len(output.items)


def test_build_image_generation_bundle_metadata_source_is_bundle() -> None:
    result = build_image_generation_bundle(make_image_generation_output())

    assert result.metadata["source"] == "image_generation_bundle"


def test_build_image_generation_bundle_metadata_provider_matches_input() -> None:
    result = build_image_generation_bundle(make_image_generation_output(provider="mock"))

    assert result.metadata["provider"] == "mock"


def test_build_image_generation_bundle_metadata_counts_are_correct() -> None:
    result = build_image_generation_bundle(make_image_generation_output())

    assert result.metadata["bundle_version"] == "v1"
    assert result.metadata["image_item_count"] == 2
    assert result.metadata["asset_count"] == 2
    assert result.metadata["task_count"] == 2


def test_build_image_generation_bundle_does_not_read_files_or_call_external_services() -> None:
    result = build_image_generation_bundle(make_image_generation_output())

    assert result.assets.assets[0].mock_url == "/mock/images/mock-img-P001-1.png"
    assert result.tasks.tasks[0].asset_ids == ["asset-mock-img-P001-1"]
    assert result.image_generation.items[0].image_url is None
