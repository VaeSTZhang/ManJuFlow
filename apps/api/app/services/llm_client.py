from typing import Any

import httpx

from app.config import get_settings


class LLMClient:
    """OpenAI-compatible chat completions client."""

    def __init__(self, timeout: float = 60.0) -> None:
        settings = get_settings()
        provider = (settings.llm_provider or "default").lower().strip() or "default"

        if provider == "default":
            base_url = settings.llm_base_url
            model = settings.llm_model
            api_key = settings.llm_api_key
            field_names = {
                "api_key": "LLM_API_KEY",
                "base_url": "LLM_BASE_URL",
                "model": "LLM_MODEL",
            }
        elif provider == "deepseek":
            base_url = settings.deepseek_base_url
            model = settings.deepseek_model
            api_key = settings.deepseek_api_key
            field_names = {
                "api_key": "DEEPSEEK_API_KEY",
                "base_url": "DEEPSEEK_BASE_URL",
                "model": "DEEPSEEK_MODEL",
            }
        elif provider == "mimo":
            base_url = settings.mimo_base_url
            model = settings.mimo_model
            api_key = settings.mimo_api_key
            field_names = {
                "api_key": "MIMO_API_KEY",
                "base_url": "MIMO_BASE_URL",
                "model": "MIMO_MODEL",
            }
        else:
            raise ValueError("LLM_PROVIDER only supports 'default', 'deepseek', or 'mimo'.")

        missing_fields = []

        if not api_key:
            missing_fields.append(field_names["api_key"])
        if not base_url:
            missing_fields.append(field_names["base_url"])
        if not model:
            missing_fields.append(field_names["model"])

        if missing_fields:
            raise ValueError(f"Missing required LLM configuration: {', '.join(missing_fields)}")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, messages: list[dict[str, str]]) -> str:
        try:
            response = httpx.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                },
                timeout=self.timeout,
            )
        except httpx.RequestError as exc:
            raise RuntimeError("LLM request failed before receiving a response.") from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"LLM request failed with status {response.status_code}.") from exc

        try:
            data: dict[str, Any] = response.json()
        except ValueError as exc:
            raise ValueError("LLM response was not valid JSON.") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("LLM response does not contain message content.") from exc

        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM response message content is empty.")

        return content
