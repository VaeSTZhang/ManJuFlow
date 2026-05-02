from pathlib import Path
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app


def make_prompt_item(**overrides) -> dict:
    data = {
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "positive_prompt": "cinematic realistic rain night hospital entrance, two characters facing each other",
        "negative_prompt": "low quality, blurry, distorted hands, watermark",
        "style_preset": "cinematic realistic",
        "aspect_ratio": "9:16",
    }
    data.update(overrides)
    return data


def make_request_payload(**overrides) -> dict:
    data = {
        "project_title": "测试短剧：雨夜重逢",
        "prompt_items": [make_prompt_item()],
    }
    data.update(overrides)
    return data


def test_generate_image_generation_bundle_endpoint_returns_200() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload())

    assert response.status_code == 200


def test_generate_image_generation_bundle_endpoint_response_contains_main_sections() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert "image_generation" in data
    assert "assets" in data
    assert "tasks" in data
    assert "metadata" in data


def test_generate_image_generation_bundle_endpoint_image_item_count_is_correct() -> None:
    client = TestClient(app)
    payload = make_request_payload(
        prompt_items=[
            make_prompt_item(prompt_id="P001", shot_id="S001_SH001"),
            make_prompt_item(prompt_id="P002", shot_id="S001_SH002"),
        ],
        output_count=2,
    )

    response = client.post("/api/images/generate-bundle", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["image_generation"]["items"]) == 4


def test_generate_image_generation_bundle_endpoint_asset_count_matches_image_items() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload())

    assert response.status_code == 200
    data = response.json()
    assert len(data["assets"]["assets"]) == len(data["image_generation"]["items"])


def test_generate_image_generation_bundle_endpoint_task_count_matches_image_items() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload())

    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]["tasks"]) == len(data["image_generation"]["items"])


def test_generate_image_generation_bundle_endpoint_asset_maps_generation_ids() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload())

    assert response.status_code == 200
    asset = response.json()["assets"]["assets"][0]
    assert asset["prompt_id"] == "P001"
    assert asset["shot_id"] == "S001_SH001"
    assert asset["task_id"] == "mock-img-P001-1"


def test_generate_image_generation_bundle_endpoint_task_maps_generation_ids() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload())

    assert response.status_code == 200
    task = response.json()["tasks"]["tasks"][0]
    assert task["task_id"] == "mock-img-P001-1"
    assert task["prompt_id"] == "P001"
    assert task["shot_id"] == "S001_SH001"


def test_generate_image_generation_bundle_endpoint_metadata_is_correct() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload())

    assert response.status_code == 200
    metadata = response.json()["metadata"]
    assert metadata["source"] == "image_generation_bundle"
    assert metadata["image_item_count"] == 1
    assert metadata["asset_count"] == 1
    assert metadata["task_count"] == 1


def test_generate_images_endpoint_still_returns_plain_image_generation_output() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate", json=make_request_payload())

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "assets" not in data
    assert "tasks" not in data


def test_generate_image_generation_bundle_endpoint_rejects_missing_prompt_items() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/images/generate-bundle",
        json={
            "project_title": "测试短剧：雨夜重逢",
        },
    )

    assert response.status_code == 422


def test_generate_image_generation_bundle_endpoint_rejects_empty_prompt_items() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload(prompt_items=[]))

    assert response.status_code == 422


def test_generate_image_generation_bundle_endpoint_rejects_output_count_greater_than_four() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate-bundle", json=make_request_payload(output_count=5))

    assert response.status_code == 422
