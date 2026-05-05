from pydantic import BaseModel, Field, field_validator


class ContextOptions(BaseModel):
    user_id: str | None = Field(None, description="内部用户 ID，可选。")
    workspace_id: str | None = Field(None, description="工作区 ID，可选。")
    project_id: str | None = Field(None, description="项目 ID，可选。")
    session_id: str | None = Field(None, description="创作或编辑会话 ID，可选。")
    request_id: str | None = Field(None, description="单次 API 请求追踪 ID，可选。")
    source_stage: str | None = Field(None, description="当前内容阶段，可选。")
    context_policy: str = Field(
        "current_project_only",
        min_length=1,
        description="上下文读取策略，默认只允许当前项目上下文。",
    )

    @field_validator(
        "user_id",
        "workspace_id",
        "project_id",
        "session_id",
        "request_id",
        "source_stage",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped_value = value.strip()
            return stripped_value or None
        return value

    @field_validator("context_policy")
    @classmethod
    def validate_context_policy(cls, value: str) -> str:
        stripped_value = value.strip()
        if stripped_value == "":
            raise ValueError("context_policy 不能为空。")
        return stripped_value
