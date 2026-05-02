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


def test_generate_images_endpoint_returns_200() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate", json=make_request_payload())

    assert response.status_code == 200


def test_generate_images_endpoint_response_contains_main_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate", json=make_request_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert data["provider"] == "mock"
    assert data["status"] == "succeeded"
    assert isinstance(data["items"], list)


def test_generate_images_endpoint_returns_one_item_for_single_prompt_and_output_count_one() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate", json=make_request_payload(output_count=1))

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_generate_images_endpoint_expands_prompt_items_by_output_count() -> None:
    client = TestClient(app)
    payload = make_request_payload(
        prompt_items=[
            make_prompt_item(prompt_id="P001", shot_id="S001_SH001"),
            make_prompt_item(prompt_id="P002", shot_id="S001_SH002"),
        ],
        output_count=2,
    )

    response = client.post("/api/images/generate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 4


def test_generate_images_endpoint_items_contain_required_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate", json=make_request_payload())

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["task_id"]
    assert item["prompt_id"] == "P001"
    assert item["shot_id"] == "S001_SH001"
    assert item["mock_url"]
    assert item["local_path"]
    assert item["positive_prompt"]
    assert item["negative_prompt"]


def test_generate_images_endpoint_uses_mock_url_and_local_path_prefixes() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate", json=make_request_payload())

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["mock_url"].startswith("/mock/images/")
    assert item["local_path"].startswith("mock_outputs/images/")


def test_generate_images_endpoint_is_available_in_openapi() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/images/generate" in response.json()["paths"]


def test_generate_images_endpoint_rejects_missing_prompt_items() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/images/generate",
        json={
            "project_title": "测试短剧：雨夜重逢",
        },
    )

    assert response.status_code == 422


def test_generate_images_endpoint_rejects_empty_prompt_items() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate", json=make_request_payload(prompt_items=[]))

    assert response.status_code == 422


def test_generate_images_endpoint_rejects_output_count_greater_than_four() -> None:
    client = TestClient(app)

    response = client.post("/api/images/generate", json=make_request_payload(output_count=5))

    assert response.status_code == 422
