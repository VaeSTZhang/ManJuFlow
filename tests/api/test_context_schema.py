from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.context import ContextOptions


def test_context_options_defaults_to_current_project_only() -> None:
    options = ContextOptions()

    assert options.context_policy == "current_project_only"


def test_context_options_accepts_context_identifiers() -> None:
    options = ContextOptions(
        user_id="user-001",
        workspace_id="workspace-001",
        project_id="project-001",
        session_id="session-001",
        request_id="request-001",
        source_stage="generated_script",
    )

    assert options.user_id == "user-001"
    assert options.workspace_id == "workspace-001"
    assert options.project_id == "project-001"
    assert options.session_id == "session-001"
    assert options.request_id == "request-001"
    assert options.source_stage == "generated_script"
    assert options.context_policy == "current_project_only"


def test_context_options_converts_empty_optional_strings_to_none() -> None:
    options = ContextOptions(
        user_id=" ",
        workspace_id="",
        project_id=" project-001 ",
    )

    assert options.user_id is None
    assert options.workspace_id is None
    assert options.project_id == "project-001"


def test_context_options_rejects_empty_context_policy() -> None:
    with pytest.raises(ValidationError):
        ContextOptions(context_policy=" ")


def test_context_options_model_dump_contains_context_policy() -> None:
    options = ContextOptions(project_id="project-001")

    dumped = options.model_dump()

    assert dumped["project_id"] == "project-001"
    assert dumped["context_policy"] == "current_project_only"
