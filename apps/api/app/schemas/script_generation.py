from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.context import ContextOptions
from app.schemas.script import CharacterProfile, EpisodeScript


ScriptSourceMode = Literal[
    "idea",
    "film_script",
    "novel",
    "assistant_rewrite",
    "uploaded_document",
]

AIRequestPurpose = Literal[
    "script_generation",
    "film_adaptation",
    "novel_adaptation",
    "assistant_chat",
    "script_rewrite",
    "quality_review",
    "storyboard_generation",
    "prompt_generation",
]


class AIRequestOptions(BaseModel):
    provider: str | None = Field(None, description="请求级模型 provider。为空时使用后端默认。")
    model: str | None = Field(None, description="请求级模型名称。为空时使用 provider 默认模型。")
    temperature: float | None = Field(None, ge=0, le=2, description="生成温度，可选。")
    max_tokens: int | None = Field(None, ge=1, description="最大输出 token，可选。")
    language: str = Field("zh", description="输出语言。")
    purpose: AIRequestPurpose = Field("script_generation", description="本次 AI 请求用途。")


class ShortDramaGenerationInput(BaseModel):
    project_title: str | None = Field(None, min_length=1, description="项目标题，可选。")
    source_mode: ScriptSourceMode = Field("idea", description="短剧剧本生成来源模式。")
    idea_text: str | None = Field(None, description="灵感文本，主要用于 idea 模式。")
    source_text: str | None = Field(None, description="来源文本，主要用于电影剧本、小说、上传文档等模式。")
    target_episode_count: int = Field(1, ge=1, le=100, description="目标短剧集数，范围 1-100。")
    genre: str = Field("短剧", min_length=1, description="内容类型或题材。")
    style: str = Field("强钩子、快节奏、适合短剧", min_length=1, description="短剧风格要求。")
    target_audience: str | None = Field(None, description="目标受众，可选。")
    duration_per_episode: str | None = Field(None, description="单集时长，可选。")
    adaptation_goal: str | None = Field(None, description="改编目标，可选。")
    key_plot_must_keep: str | None = Field(None, description="必须保留的关键剧情，可选。")
    main_characters: str | None = Field(None, description="主要人物说明，可选。")
    key_relationships: str | None = Field(None, description="关键人物关系，可选。")
    extra_requirements: str | None = Field(None, description="额外要求，可选。")
    language: str = Field("zh", min_length=1, description="输出语言，默认中文。")
    workspace_id: str | None = Field(None, min_length=1, description="工作区 ID，可选。")
    project_id: str | None = Field(None, min_length=1, description="项目 ID，可选。")
    session_id: str | None = Field(None, min_length=1, description="会话 ID，可选。")
    user_id: str | None = Field(None, min_length=1, description="用户 ID，可选。")
    ai_options: AIRequestOptions | None = Field(None, description="请求级 AI 模型与生成选项。")
    context_options: ContextOptions | None = Field(
        None,
        description="请求级上下文归属信息，用于记录 user/workspace/project/session 边界。",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元信息。")


class AdaptationNotes(BaseModel):
    source_mode: ScriptSourceMode = Field(..., description="改编来源模式。")
    adaptation_strategy: str | None = Field(None, description="改编策略说明，可选。")
    preserved_elements: list[str] = Field(default_factory=list, description="保留元素列表。")
    changed_elements: list[str] = Field(default_factory=list, description="调整元素列表。")
    short_drama_hooks: list[str] = Field(default_factory=list, description="短剧钩子建议列表。")
    risk_notes: list[str] = Field(default_factory=list, description="风险提示列表。")


class ShortDramaScriptOutput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    source_mode: ScriptSourceMode = Field(..., description="短剧剧本来源模式。")
    logline: str = Field(..., min_length=1, description="一句话故事梗概。")
    world_setting: str = Field(..., min_length=1, description="故事世界观或背景设定。")
    characters: list[CharacterProfile] = Field(default_factory=list, description="主要角色列表。")
    adaptation_notes: AdaptationNotes | None = Field(None, description="改编说明，可选。")
    episode_count: int = Field(..., ge=1, description="分集数量。")
    episodes: list[EpisodeScript] = Field(default_factory=list, description="分集剧本列表。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元信息。")
