from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.services.script_generation import (  # noqa: E402
    get_script_generation_entry,
    get_supported_source_modes,
    list_script_generation_entries,
)
from app.services.script_input_limits import (  # noqa: E402
    MAX_IDEA_TEXT_CHARS,
    MAX_SCRIPT_TEXT_CHARS,
)


def test_list_script_generation_entries_returns_all_default_entries() -> None:
    entries = list_script_generation_entries()

    assert len(entries) >= 5


def test_get_supported_source_modes_contains_core_entries() -> None:
    source_modes = get_supported_source_modes()

    assert "idea" in source_modes
    assert "film_script" in source_modes
    assert "novel" in source_modes


def test_get_script_generation_entry_returns_idea_config() -> None:
    entry = get_script_generation_entry("idea")

    assert entry.source_mode == "idea"
    assert entry.label == "灵感生成短剧"
    assert entry.supports_mock is True
    assert entry.supports_llm is True


def test_film_script_prompt_template_name_contains_film() -> None:
    entry = get_script_generation_entry("film_script")

    assert "film" in entry.prompt_template_name
    assert entry.source_mode == "film_script"


def test_novel_prompt_template_name_contains_novel() -> None:
    entry = get_script_generation_entry("novel")

    assert "novel" in entry.prompt_template_name
    assert entry.source_mode == "novel"


def test_idea_max_input_chars_uses_idea_limit() -> None:
    entry = get_script_generation_entry("idea")

    assert entry.max_input_chars == MAX_IDEA_TEXT_CHARS


def test_film_script_max_input_chars_uses_script_text_limit() -> None:
    entry = get_script_generation_entry("film_script")

    assert entry.max_input_chars == MAX_SCRIPT_TEXT_CHARS


def test_each_entry_has_next_actions() -> None:
    for entry in list_script_generation_entries():
        assert entry.next_actions is not None
        assert len(entry.next_actions) > 0
        assert "edit_script" in entry.next_actions


def test_unknown_source_mode_raises_value_error() -> None:
    with pytest.raises(ValueError) as exc_info:
        get_script_generation_entry("unknown")

    assert "Unknown script generation source_mode" in str(exc_info.value)
    assert "idea" in str(exc_info.value)
