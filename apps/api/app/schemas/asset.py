from typing import Any

from pydantic import BaseModel, Field


class AssetItem(BaseModel):
    asset_id: str = Field(..., min_length=1, description="资产唯一标识。")
    asset_type: str = Field("image", min_length=1, description="资产类型，例如 image。")
    project_title: str | None = Field(None, description="项目标题，可选。")
    prompt_id: str | None = Field(None, description="对应的绘图 Prompt ID，可选。")
    shot_id: str | None = Field(None, description="对应的分镜镜头 ID，可选。")
    task_id: str | None = Field(None, description="对应的渲染任务 ID，可选。")
    provider: str = Field("mock", min_length=1, description="资产来源 provider。")
    status: str = Field("available", min_length=1, description="资产状态。")
    url: str | None = Field(None, description="真实资产 URL，可选。")
    mock_url: str | None = Field(None, description="mock 占位资产 URL，可选。")
    local_path: str | None = Field(None, description="本地路径占位，可选。")
    width: int | None = Field(None, ge=1, description="资产宽度，可选。")
    height: int | None = Field(None, ge=1, description="资产高度，可选。")
    seed: int | None = Field(None, description="生成资产使用的随机种子，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="资产扩展元信息。")
    created_at: str | None = Field(None, description="资产创建时间，可选。")
    notes: str | None = Field(None, description="资产备注，可选。")


class AssetCollection(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    assets: list[AssetItem] = Field(default_factory=list, description="资产列表，可为空。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="资产集合扩展元信息。")
