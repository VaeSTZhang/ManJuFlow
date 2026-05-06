from typing import Literal

from pydantic import BaseModel, Field, field_validator


UserRole = Literal["admin", "creator", "reviewer", "viewer"]
UserStatus = Literal["active", "disabled", "pending"]
AuthMetadataValue = str | int | float | bool | None


def _strip_required_string(value: str, field_name: str) -> str:
    stripped_value = value.strip()
    if stripped_value == "":
        raise ValueError(f"{field_name} 不能为空。")
    return stripped_value


class InternalUser(BaseModel):
    user_id: str = Field(..., min_length=1, description="内部用户 ID。")
    username: str = Field(..., min_length=1, description="内部登录用户名，支持中文和英文。")
    display_name: str | None = Field(None, description="用户展示名，可选。")
    role: UserRole = Field("creator", description="内部用户角色。")
    status: UserStatus = Field("active", description="内部用户状态。")
    workspace_id: str | None = Field(None, description="默认工作区 ID，可选。")
    created_at: str | None = Field(None, description="创建时间，可选。")
    updated_at: str | None = Field(None, description="更新时间，可选。")
    metadata: dict[str, AuthMetadataValue] = Field(
        default_factory=dict,
        description="安全扩展元信息，不应包含密码、token 或真实敏感信息。",
    )

    @field_validator("user_id", "username")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return _strip_required_string(value, info.field_name)

    @field_validator("display_name", "workspace_id", "created_at", "updated_at", mode="before")
    @classmethod
    def empty_optional_string_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped_value = value.strip()
            return stripped_value or None
        return value


class AuthLoginInput(BaseModel):
    username: str = Field(..., min_length=1, description="登录用户名。")
    password: str = Field(..., min_length=1, description="登录密码。")

    @field_validator("username", "password")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return _strip_required_string(value, info.field_name)


class AuthSession(BaseModel):
    session_id: str = Field(..., min_length=1, description="内部会话 ID。")
    user_id: str = Field(..., min_length=1, description="内部用户 ID。")
    workspace_id: str | None = Field(None, description="会话绑定工作区 ID，可选。")
    role: UserRole = Field(..., description="会话用户角色。")
    status: UserStatus = Field(..., description="会话用户状态。")
    expires_at: str | None = Field(None, description="会话过期时间，可选。")
    context_policy: str = Field(
        "current_project_only",
        min_length=1,
        description="默认上下文策略。",
    )

    @field_validator("session_id", "user_id", "context_policy")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return _strip_required_string(value, info.field_name)

    @field_validator("workspace_id", "expires_at", mode="before")
    @classmethod
    def empty_optional_string_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped_value = value.strip()
            return stripped_value or None
        return value


class AuthLoginOutput(BaseModel):
    user: InternalUser = Field(..., description="当前登录用户。")
    session: AuthSession = Field(..., description="当前登录会话。")
    access_token: str | None = Field(None, description="访问 token，可选。")
    token_type: str = Field("bearer", min_length=1, description="token 类型，默认 bearer。")

    @field_validator("access_token", mode="before")
    @classmethod
    def empty_token_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped_value = value.strip()
            return stripped_value or None
        return value

    @field_validator("token_type")
    @classmethod
    def validate_token_type(cls, value: str) -> str:
        return _strip_required_string(value, "token_type")
