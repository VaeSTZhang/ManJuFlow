from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.asset import AssetCollection, AssetItem


def make_asset_item(**overrides) -> AssetItem:
    data = {
        "asset_id": "ASSET_001",
        "project_title": "测试短剧：雨夜重逢",
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "task_id": "mock-img-P001-1",
        "mock_url": "/mock/images/mock-img-P001-1.png",
        "local_path": "mock_outputs/images/mock-img-P001-1.png",
        "width": 1080,
        "height": 1920,
        "seed": 101,
    }
    data.update(overrides)
    return AssetItem(**data)


def test_asset_item_can_be_created() -> None:
    asset = make_asset_item()

    assert asset.asset_id == "ASSET_001"
    assert asset.project_title == "测试短剧：雨夜重逢"


def test_asset_item_defaults_asset_type_to_image() -> None:
    asset = AssetItem(asset_id="ASSET_001")

    assert asset.asset_type == "image"


def test_asset_item_defaults_provider_to_mock() -> None:
    asset = AssetItem(asset_id="ASSET_001")

    assert asset.provider == "mock"


def test_asset_item_can_include_mock_paths_dimensions_and_seed() -> None:
    asset = make_asset_item()

    assert asset.mock_url == "/mock/images/mock-img-P001-1.png"
    assert asset.local_path == "mock_outputs/images/mock-img-P001-1.png"
    assert asset.width == 1080
    assert asset.height == 1920
    assert asset.seed == 101


def test_asset_item_rejects_non_positive_width() -> None:
    with pytest.raises(ValidationError):
        make_asset_item(width=0)


def test_asset_item_rejects_non_positive_height() -> None:
    with pytest.raises(ValidationError):
        make_asset_item(height=0)


def test_asset_collection_can_include_multiple_assets() -> None:
    collection = AssetCollection(
        project_title="测试短剧：雨夜重逢",
        assets=[
            make_asset_item(asset_id="ASSET_001"),
            make_asset_item(asset_id="ASSET_002", prompt_id="P002", shot_id="S001_SH002"),
        ],
    )

    assert len(collection.assets) == 2


def test_asset_collection_model_dump_contains_project_title_and_assets() -> None:
    collection = AssetCollection(project_title="测试短剧：雨夜重逢", assets=[make_asset_item()])

    data = collection.model_dump()

    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert len(data["assets"]) == 1


def test_asset_item_rejects_empty_asset_id() -> None:
    with pytest.raises(ValidationError):
        AssetItem(asset_id="")
