from typing import Any

from pydantic import BaseModel, Field


class ImageGenerationPromptItem(BaseModel):
    prompt_id: str = Field(..., min_length=1, description="绘图 Prompt 唯一标识。")
    shot_id: str = Field(..., min_length=1, description="对应的分镜镜头唯一标识。")
    positive_prompt: str = Field(..., min_length=1, description="正向绘图 Prompt。")
    negative_prompt: str = Field(..., min_length=1, description="反向绘图 Prompt。")
    style_preset: str = Field("cinematic realistic", min_length=1, description="本条 Prompt 的绘图风格预设。")
    aspect_ratio: str = Field("9:16", min_length=1, description="本条 Prompt 的画面比例。")
    model_hint: str | None = Field(None, description="面向图片生成 provider 的模型提示，可选。")
    seed: int | None = Field(None, description="随机种子，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元信息。")


class ImageGenerationInput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    prompt_items: list[ImageGenerationPromptItem] = Field(..., min_length=1, description="绘图 Prompt 条目列表。")
    provider: str = Field("mock", min_length=1, description="图片生成 provider，默认使用 mock。")
    workflow_name: str = Field(
        "mock_image_generation_v1",
        min_length=1,
        description="图片生成 workflow 名称或占位标识。",
    )
    style_preset: str = Field("cinematic realistic", min_length=1, description="整体图片生成风格预设。")
    aspect_ratio: str = Field("9:16", min_length=1, description="目标画面比例。")
    output_count: int = Field(1, ge=1, le=4, description="每条 Prompt 期望生成的图片数量，范围 1 到 4。")
    seed: int | None = Field(None, description="全局随机种子，可选。")
    extra_parameters: dict[str, Any] = Field(default_factory=dict, description="图片生成扩展参数。")


class ImageGenerationItem(BaseModel):
    task_id: str = Field(..., min_length=1, description="图片生成任务唯一标识。")
    prompt_id: str = Field(..., min_length=1, description="对应的绘图 Prompt ID。")
    shot_id: str = Field(..., min_length=1, description="对应的分镜镜头 ID。")
    status: str = Field("succeeded", min_length=1, description="生成任务状态。")
    positive_prompt: str = Field(..., min_length=1, description="本次生成使用的正向 Prompt。")
    negative_prompt: str = Field(..., min_length=1, description="本次生成使用的反向 Prompt。")
    provider: str = Field("mock", min_length=1, description="图片生成 provider。")
    workflow_name: str = Field(
        "mock_image_generation_v1",
        min_length=1,
        description="图片生成 workflow 名称或占位标识。",
    )
    image_url: str | None = Field(None, description="真实图片 URL，可选。")
    mock_url: str | None = Field(None, description="mock 占位图片 URL，可选。")
    local_path: str | None = Field(None, description="本地文件路径占位，可选。")
    width: int | None = Field(None, ge=1, description="图片宽度，可选。")
    height: int | None = Field(None, ge=1, description="图片高度，可选。")
    seed: int | None = Field(None, description="本次生成使用的随机种子，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="生成结果扩展元信息。")
    error_message: str | None = Field(None, description="失败原因，可选。")


class ImageGenerationOutput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    provider: str = Field("mock", min_length=1, description="图片生成 provider。")
    status: str = Field("succeeded", min_length=1, description="整体生成状态。")
    items: list[ImageGenerationItem] = Field(..., min_length=1, description="图片生成结果列表。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="整体扩展元信息。")
