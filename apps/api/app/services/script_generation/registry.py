from dataclasses import dataclass

from app.schemas.script_generation import ScriptSourceMode
from app.services.script_input_limits import (
    MAX_EXTRACTED_TEXT_CHARS,
    MAX_IDEA_TEXT_CHARS,
    MAX_SCRIPT_TEXT_CHARS,
)


MAX_ASSISTANT_REWRITE_INPUT_CHARS = 20_000
DEFAULT_NEXT_ACTIONS = [
    "edit_script",
    "export_document",
    "enter_prompt_workflow",
    "ask_assistant",
]


@dataclass(frozen=True)
class ScriptGenerationEntryConfig:
    source_mode: ScriptSourceMode
    label: str
    description: str
    prompt_template_name: str
    max_input_chars: int
    supports_mock: bool = True
    supports_llm: bool = True
    next_actions: list[str] | None = None

    def __post_init__(self) -> None:
        if self.next_actions is None:
            object.__setattr__(self, "next_actions", list(DEFAULT_NEXT_ACTIONS))


DEFAULT_SCRIPT_GENERATION_REGISTRY: dict[str, ScriptGenerationEntryConfig] = {
    "idea": ScriptGenerationEntryConfig(
        source_mode="idea",
        label="灵感生成短剧",
        description="从一句创意或故事想法生成短剧剧本。",
        prompt_template_name="idea_to_short_drama_script_v1.md",
        max_input_chars=MAX_IDEA_TEXT_CHARS,
    ),
    "film_script": ScriptGenerationEntryConfig(
        source_mode="film_script",
        label="电影剧本改短剧",
        description="将电影剧本、长剧本或影视分场文本改编为短剧剧本。",
        prompt_template_name="film_script_to_short_drama_v1.md",
        max_input_chars=MAX_SCRIPT_TEXT_CHARS,
    ),
    "novel": ScriptGenerationEntryConfig(
        source_mode="novel",
        label="小说改短剧",
        description="将小说、网文或故事文本改编为短剧剧本。",
        prompt_template_name="novel_to_short_drama_v1.md",
        max_input_chars=MAX_SCRIPT_TEXT_CHARS,
    ),
    "assistant_rewrite": ScriptGenerationEntryConfig(
        source_mode="assistant_rewrite",
        label="Assistant 改写短剧",
        description="由 AI Assistant 辅助改写或增强当前短剧剧本。",
        prompt_template_name="assistant_rewrite_short_drama_v1.md",
        max_input_chars=MAX_ASSISTANT_REWRITE_INPUT_CHARS,
    ),
    "uploaded_document": ScriptGenerationEntryConfig(
        source_mode="uploaded_document",
        label="上传文档生成短剧",
        description="从上传文档提取文本后生成或改编短剧剧本。",
        prompt_template_name="uploaded_document_to_short_drama_v1.md",
        max_input_chars=MAX_EXTRACTED_TEXT_CHARS,
    ),
}


def get_script_generation_entry(source_mode: ScriptSourceMode) -> ScriptGenerationEntryConfig:
    try:
        return DEFAULT_SCRIPT_GENERATION_REGISTRY[source_mode]
    except KeyError as exc:
        supported_modes = ", ".join(get_supported_source_modes())
        raise ValueError(
            f"Unknown script generation source_mode: {source_mode}. "
            f"Supported source_mode values: {supported_modes}."
        ) from exc


def list_script_generation_entries() -> list[ScriptGenerationEntryConfig]:
    return list(DEFAULT_SCRIPT_GENERATION_REGISTRY.values())


def get_supported_source_modes() -> list[str]:
    return list(DEFAULT_SCRIPT_GENERATION_REGISTRY.keys())
