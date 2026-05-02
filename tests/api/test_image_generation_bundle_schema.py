from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.asset import AssetCollection, AssetItem
from app.schemas.image_generation import ImageGenerationItem, ImageGenerationOutput
from app.schemas.image_generation_bundle import ImageGenerationBundleOutput
from app.schemas.render_task import RenderTaskItem, RenderTaskOutput


def make_image_generation_output() -> ImageGenerationOutput:
    return ImageGenerationOutput(
        project_title="测试短剧：雨夜重逢",
        provider="mock",
        items=[
            ImageGenerationItem(
                task_id="mock-img-P001-1",
                prompt_id="P001",
                shot_id="S001_SH001",
                positive_prompt="cinematic realistic rain night hospital entrance",
                negative_prompt="low quality, blurry, watermark",
                mock_url="/mock/images/mock-img-P001-1.png",
                local_path="mock_outputs/images/mock-img-P001-1.png",
            )
        ],
    )


def make_asset_collection() -> AssetCollection:
    return AssetCollection(
        project_title="测试短剧：雨夜重逢",
        assets=[AssetItem(asset_id="asset-mock-img-P001-1")],
    )


def make_render_task_output() -> RenderTaskOutput:
    return RenderTaskOutput(
        project_title="测试短剧：雨夜重逢",
        tasks=[RenderTaskItem(task_id="mock-img-P001-1")],
    )


def test_image_generation_bundle_output_can_be_created() -> None:
    image_generation = make_image_generation_output()
    bundle = ImageGenerationBundleOutput(
        project_title=image_generation.project_title,
        image_generation=image_generation,
        assets=make_asset_collection(),
        tasks=make_render_task_output(),
    )

    assert bundle.project_title == "测试短剧：雨夜重逢"


def test_image_generation_bundle_project_title_matches_image_generation() -> None:
    image_generation = make_image_generation_output()
    bundle = ImageGenerationBundleOutput(
        project_title=image_generation.project_title,
        image_generation=image_generation,
        assets=make_asset_collection(),
        tasks=make_render_task_output(),
    )

    assert bundle.project_title == bundle.image_generation.project_title


def test_image_generation_bundle_contains_asset_collection() -> None:
    bundle = ImageGenerationBundleOutput(
        project_title="测试短剧：雨夜重逢",
        image_generation=make_image_generation_output(),
        assets=make_asset_collection(),
        tasks=make_render_task_output(),
    )

    assert isinstance(bundle.assets, AssetCollection)


def test_image_generation_bundle_contains_render_task_output() -> None:
    bundle = ImageGenerationBundleOutput(
        project_title="测试短剧：雨夜重逢",
        image_generation=make_image_generation_output(),
        assets=make_asset_collection(),
        tasks=make_render_task_output(),
    )

    assert isinstance(bundle.tasks, RenderTaskOutput)


def test_image_generation_bundle_model_dump_contains_main_sections() -> None:
    bundle = ImageGenerationBundleOutput(
        project_title="测试短剧：雨夜重逢",
        image_generation=make_image_generation_output(),
        assets=make_asset_collection(),
        tasks=make_render_task_output(),
        metadata={"source": "image_generation_bundle"},
    )

    data = bundle.model_dump()

    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert "image_generation" in data
    assert "assets" in data
    assert "tasks" in data
    assert data["metadata"]["source"] == "image_generation_bundle"
