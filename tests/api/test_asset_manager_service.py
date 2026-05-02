from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.asset import AssetCollection
from app.schemas.image_generation import ImageGenerationItem, ImageGenerationOutput
from app.services.asset_manager_service import build_asset_collection_from_image_generation


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
        "image_url": None,
        "mock_url": "/mock/images/mock-img-P001-1.png",
        "local_path": "mock_outputs/images/mock-img-P001-1.png",
        "width": 1080,
        "height": 1920,
        "seed": 101,
        "metadata": {"source": "mock", "output_index": 1},
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


def test_build_asset_collection_from_image_generation_returns_asset_collection() -> None:
    result = build_asset_collection_from_image_generation(make_image_generation_output())

    assert isinstance(result, AssetCollection)


def test_build_asset_collection_keeps_project_title() -> None:
    output = make_image_generation_output()

    result = build_asset_collection_from_image_generation(output)

    assert result.project_title == output.project_title


def test_build_asset_collection_asset_count_matches_generation_items() -> None:
    output = make_image_generation_output(
        items=[
            make_image_generation_item(task_id="mock-img-P001-1", prompt_id="P001", shot_id="S001_SH001"),
            make_image_generation_item(task_id="mock-img-P002-1", prompt_id="P002", shot_id="S001_SH002"),
        ]
    )

    result = build_asset_collection_from_image_generation(output)

    assert len(result.assets) == 2


def test_build_asset_collection_uses_task_id_for_stable_asset_id() -> None:
    result = build_asset_collection_from_image_generation(make_image_generation_output())

    assert result.assets[0].asset_id == "asset-mock-img-P001-1"


def test_build_asset_collection_maps_prompt_shot_and_task_ids() -> None:
    result = build_asset_collection_from_image_generation(make_image_generation_output())
    asset = result.assets[0]

    assert asset.prompt_id == "P001"
    assert asset.shot_id == "S001_SH001"
    assert asset.task_id == "mock-img-P001-1"


def test_build_asset_collection_maps_mock_paths_dimensions_and_seed() -> None:
    result = build_asset_collection_from_image_generation(make_image_generation_output())
    asset = result.assets[0]

    assert asset.mock_url == "/mock/images/mock-img-P001-1.png"
    assert asset.local_path == "mock_outputs/images/mock-img-P001-1.png"
    assert asset.width == 1080
    assert asset.height == 1920
    assert asset.seed == 101


def test_build_asset_collection_maps_succeeded_status_to_available() -> None:
    result = build_asset_collection_from_image_generation(make_image_generation_output())

    assert result.assets[0].status == "available"


def test_build_asset_collection_keeps_failed_status() -> None:
    output = make_image_generation_output(
        status="failed",
        items=[make_image_generation_item(status="failed")],
    )

    result = build_asset_collection_from_image_generation(output)

    assert result.assets[0].status == "failed"


def test_build_asset_collection_metadata_contains_source_provider_and_count() -> None:
    result = build_asset_collection_from_image_generation(make_image_generation_output())

    assert result.metadata["source"] == "image_generation"
    assert result.metadata["provider"] == "mock"
    assert result.metadata["item_count"] == 1


def test_build_asset_collection_item_metadata_keeps_source_and_workflow() -> None:
    result = build_asset_collection_from_image_generation(make_image_generation_output())
    asset = result.assets[0]

    assert asset.metadata["source"] == "mock"
    assert asset.metadata["source_task_status"] == "succeeded"
    assert asset.metadata["workflow_name"] == "mock_image_generation_v1"


def test_build_asset_collection_does_not_read_files_or_call_external_services() -> None:
    result = build_asset_collection_from_image_generation(make_image_generation_output())
    asset = result.assets[0]

    assert asset.url is None
    assert asset.mock_url == "/mock/images/mock-img-P001-1.png"
    assert asset.local_path == "mock_outputs/images/mock-img-P001-1.png"
    assert asset.notes == "Generated from ImageGenerationOutput mock result."
