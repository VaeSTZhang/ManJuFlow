from typing import Any

from pydantic import BaseModel, Field


class RenderTaskItem(BaseModel):
    task_id: str = Field(..., min_length=1, description="渲染任务唯一标识。")
    task_type: str = Field("image_generation", min_length=1, description="任务类型。")
    project_title: str | None = Field(None, description="项目标题，可选。")
    prompt_id: str | None = Field(None, description="对应的绘图 Prompt ID，可选。")
    shot_id: str | None = Field(None, description="对应的分镜镜头 ID，可选。")
    provider: str = Field("mock", min_length=1, description="任务 provider。")
    workflow_name: str | None = Field(None, description="任务使用的 workflow 逻辑名称，可选。")
    status: str = Field("succeeded", min_length=1, description="任务状态。")
    progress: float | None = Field(None, ge=0, le=1, description="任务进度，范围 0 到 1，可选。")
    asset_ids: list[str] = Field(default_factory=list, description="任务关联的资产 ID 列表。")
    error_code: str | None = Field(None, description="错误代码，可选。")
    error_message: str | None = Field(None, description="错误信息，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="任务扩展元信息。")
    created_at: str | None = Field(None, description="任务创建时间，可选。")
    updated_at: str | None = Field(None, description="任务更新时间，可选。")


class RenderTaskOutput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    tasks: list[RenderTaskItem] = Field(default_factory=list, description="渲染任务列表，可为空。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="渲染任务集合扩展元信息。")
