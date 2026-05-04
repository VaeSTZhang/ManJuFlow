from typing import Any

from pydantic import BaseModel, Field, model_validator


class ExistingScriptInput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    script_text: str | None = Field(None, description="用户粘贴或上传文件提取后的已有剧本文本。")
    source_id: str | None = Field(None, min_length=1, description="已保存上传源的唯一标识，可选。")
    source_type: str = Field("pasted_text", min_length=1, description="剧本来源类型，例如 pasted_text 或 uploaded_file。")
    target_segment_level: str = Field("scene", min_length=1, description="目标切分粒度，例如 scene。")
    language: str = Field("zh", min_length=1, description="剧本文本语言。")
    extra_requirements: str | None = Field(None, description="额外切分要求，可选。")
    workspace_id: str | None = Field(None, min_length=1, description="工作区 ID，可选。")
    user_id: str | None = Field(None, min_length=1, description="公司用户 ID，可选。")
    ai_account_id: str | None = Field(None, min_length=1, description="Dramora 内部创作功能账户 ID，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元信息。")

    @model_validator(mode="after")
    def validate_script_source(self) -> "ExistingScriptInput":
        has_script_text = self.script_text is not None and self.script_text.strip() != ""
        has_source_id = self.source_id is not None and self.source_id.strip() != ""

        if not has_script_text and not has_source_id:
            raise ValueError("script_text 或 source_id 至少需要提供一个。")

        if self.script_text is not None:
            self.script_text = self.script_text.strip()

        return self


class ScriptSegment(BaseModel):
    segment_id: str = Field(..., min_length=1, description="切分片段唯一标识。")
    episode_number: int | None = Field(None, ge=1, description="所属集数编号，可选。")
    scene_number: int | None = Field(None, ge=1, description="所属场次编号，可选。")
    segment_type: str = Field("scene", min_length=1, description="片段类型，例如 scene。")
    title: str = Field(..., min_length=1, description="片段标题。")
    original_text: str = Field(..., min_length=1, description="该片段对应的原始剧本文本。")
    summary: str = Field(..., min_length=1, description="该片段摘要。")
    characters: list[str] = Field(default_factory=list, description="该片段涉及角色列表。")
    location: str | None = Field(None, description="场景地点，可选。")
    time_of_day: str | None = Field(None, description="场景时间，可选。")
    conflict: str | None = Field(None, description="该片段的核心冲突，可选。")
    emotion: str | None = Field(None, description="该片段的情绪重点，可选。")
    visual_notes: str | None = Field(None, description="面向分镜或绘图 Prompt 的视觉备注，可选。")
    dialogue_text: str | None = Field(None, description="该片段对白文本，可选。")
    estimated_duration_seconds: float | None = Field(None, ge=0, description="预计时长，单位秒，可选。")
    next_step_hint: str | None = Field(None, description="后续进入分镜或 Prompt 阶段的提示，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元信息。")


class ScriptSegmentationOutput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    segmentation_summary: str = Field(..., min_length=1, description="剧本切分结果摘要。")
    segment_count: int = Field(..., ge=1, description="切分片段数量。")
    segments: list[ScriptSegment] = Field(..., min_length=1, description="切分片段列表。")
    source_id: str | None = Field(None, min_length=1, description="关联的上传源唯一标识，可选。")
    workspace_id: str | None = Field(None, min_length=1, description="工作区 ID，可选。")
    user_id: str | None = Field(None, min_length=1, description="公司用户 ID，可选。")
    ai_account_id: str | None = Field(None, min_length=1, description="Dramora 内部创作功能账户 ID，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元信息。")

    @model_validator(mode="after")
    def validate_segment_count(self) -> "ScriptSegmentationOutput":
        if self.segment_count != len(self.segments):
            raise ValueError("segment_count 需要与 segments 数量一致。")
        return self
