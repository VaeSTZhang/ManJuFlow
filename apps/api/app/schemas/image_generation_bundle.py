from typing import Any

from pydantic import BaseModel, Field

from app.schemas.asset import AssetCollection
from app.schemas.image_generation import ImageGenerationOutput
from app.schemas.render_task import RenderTaskOutput


class ImageGenerationBundleOutput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    image_generation: ImageGenerationOutput = Field(..., description="图片生成原始输出。")
    assets: AssetCollection = Field(..., description="由图片生成结果转换出的资产集合。")
    tasks: RenderTaskOutput = Field(..., description="由图片生成结果转换出的任务状态集合。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="结果包扩展元信息。")
