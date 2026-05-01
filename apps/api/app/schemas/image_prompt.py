from typing import Any

from pydantic import BaseModel, Field, model_validator


class ImagePromptInput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    storyboard_summary: str | None = Field(None, description="分镜整体摘要，可选。")
    storyboard: dict[str, Any] | None = Field(None, description="结构化分镜数据，可选。")
    storyboard_text: str | None = Field(None, min_length=1, description="分镜文本内容，可选。")
    target_model: str = Field("general", min_length=1, description="目标绘图模型或模型类型。")
    aspect_ratio: str = Field("9:16", min_length=1, description="目标画面比例。")
    style_preset: str = Field("cinematic realistic", min_length=1, description="整体绘图风格预设。")
    language: str = Field("en", min_length=1, description="生成 Prompt 使用的语言。")
    extra_requirements: str | None = Field(None, description="额外绘图 Prompt 要求。")
    llm_provider: str | None = Field(None, description="请求级 LLM provider 覆盖；不传时使用后端默认配置。")
    llm_model: str | None = Field(None, description="请求级 LLM model 覆盖；不传时使用当前 provider 默认模型。")

    @model_validator(mode="after")
    def validate_storyboard_source(self) -> "ImagePromptInput":
        if self.storyboard is None and self.storyboard_text is None:
            raise ValueError("storyboard 或 storyboard_text 至少需要提供一个。")
        return self


class ImagePromptItem(BaseModel):
    prompt_id: str = Field(..., min_length=1, description="绘图 Prompt 唯一标识。")
    shot_id: str = Field(..., min_length=1, description="对应的分镜镜头唯一标识。")
    scene_id: str | None = Field(None, description="对应的场景唯一标识，可选。")
    shot_number: int | None = Field(None, ge=1, description="镜头编号，可选，必须大于等于 1。")
    scene_number: int | None = Field(None, ge=1, description="场次编号，可选，必须大于等于 1。")
    source_visual_description: str | None = Field(None, description="来自分镜阶段的原始画面描述。")
    positive_prompt: str = Field(..., min_length=1, description="正向绘图 Prompt。")
    negative_prompt: str = Field(..., min_length=1, description="反向绘图 Prompt。")
    style_preset: str = Field("cinematic realistic", min_length=1, description="本条 Prompt 的绘图风格预设。")
    aspect_ratio: str = Field("9:16", min_length=1, description="本条 Prompt 的画面比例。")
    camera_language: str | None = Field(None, description="镜头语言描述，可选。")
    lighting: str | None = Field(None, description="光照与氛围描述，可选。")
    color_palette: str | None = Field(None, description="色彩方案描述，可选。")
    character_consistency: str | None = Field(None, description="角色一致性要求，可选。")
    environment: str | None = Field(None, description="场景环境描述，可选。")
    composition: str | None = Field(None, description="构图要求，可选。")
    model_hint: str | None = Field(None, description="面向目标绘图模型的提示，可选。")
    seed: int | None = Field(None, description="随机种子，可选。")
    notes: str | None = Field(None, description="补充说明，可选。")


class ImagePromptOutput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    prompt_summary: str = Field(..., min_length=1, description="绘图 Prompt 生成结果摘要。")
    target_model: str = Field("general", min_length=1, description="目标绘图模型或模型类型。")
    aspect_ratio: str = Field("9:16", min_length=1, description="整体画面比例。")
    style_preset: str = Field("cinematic realistic", min_length=1, description="整体绘图风格预设。")
    items: list[ImagePromptItem] = Field(..., min_length=1, description="绘图 Prompt 条目列表。")
