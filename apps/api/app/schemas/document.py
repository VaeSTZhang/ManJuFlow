from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.context import ContextOptions


DocumentExportFormat = Literal["txt", "json", "docx"]
DocumentSourceStage = Literal[
    "script",
    "script_segmentation",
    "storyboard",
    "image_prompt",
    "assistant",
    "other",
]


class DocumentExportInput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    document_type: str = Field("creative_document", min_length=1, description="导出文档类型。")
    source_stage: DocumentSourceStage = Field("script", description="文档来源阶段。")
    content_text: str | None = Field(None, description="待导出的纯文本内容，可选。")
    structured_payload: dict[str, Any] | None = Field(None, description="待导出的结构化内容，可选。")
    export_format: DocumentExportFormat = Field("txt", description="导出格式，支持 txt / json / docx。")
    filename: str | None = Field(None, min_length=1, description="导出文件名，可选，后续 service 可自动生成。")
    workspace_id: str | None = Field(None, min_length=1, description="工作区 ID，可选。")
    project_id: str | None = Field(None, min_length=1, description="项目 ID，可选。")
    session_id: str | None = Field(None, min_length=1, description="会话 ID，可选。")
    context_options: ContextOptions | None = Field(
        None,
        description="导出请求归属的 user/workspace/project/session 上下文，可选。",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="导出请求扩展元信息。")


class DocumentExportOutput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    document_type: str = Field(..., min_length=1, description="导出文档类型。")
    source_stage: DocumentSourceStage = Field(..., description="文档来源阶段。")
    export_format: DocumentExportFormat = Field(..., description="导出格式。")
    filename: str = Field(..., min_length=1, description="导出文件名。")
    content_text: str | None = Field(None, description="导出的文本内容或预览，可选。")
    download_url: str | None = Field(None, description="下载地址，可选。")
    file_size_bytes: int | None = Field(None, ge=0, description="导出文件大小，单位字节，可选。")
    workspace_id: str | None = Field(None, min_length=1, description="工作区 ID，可选。")
    project_id: str | None = Field(None, min_length=1, description="项目 ID，可选。")
    session_id: str | None = Field(None, min_length=1, description="会话 ID，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="导出结果扩展元信息。")
