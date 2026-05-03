from typing import Any

from pydantic import BaseModel, Field, field_validator


class UploadSourceInput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    source_type: str = Field("script_docx", min_length=1, description="上传源类型，默认支持剧本 .docx。")
    workspace_id: str | None = Field(None, min_length=1, description="工作区 ID，可选。")
    project_id: str | None = Field(None, min_length=1, description="项目 ID，可选。")
    user_id: str | None = Field(None, min_length=1, description="公司用户 ID，可选。")
    ai_account_id: str | None = Field(None, min_length=1, description="ManJuFlow 内部 AI 功能账户 ID，可选。")
    language: str = Field("zh", min_length=1, description="上传剧本文档语言。")
    extra_requirements: str | None = Field(None, description="额外解析或切分要求，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="上传源扩展元信息。")

    @field_validator("project_title")
    @classmethod
    def validate_project_title(cls, value: str) -> str:
        stripped_value = value.strip()
        if stripped_value == "":
            raise ValueError("project_title 不能为空。")
        return stripped_value


class UploadSourceMetadata(BaseModel):
    source_id: str = Field(..., min_length=1, description="上传源唯一标识。")
    project_title: str = Field(..., min_length=1, description="项目标题。")
    project_id: str | None = Field(None, min_length=1, description="项目 ID，可选。")
    workspace_id: str | None = Field(None, min_length=1, description="工作区 ID，可选。")
    user_id: str | None = Field(None, min_length=1, description="公司用户 ID，可选。")
    ai_account_id: str | None = Field(None, min_length=1, description="ManJuFlow 内部 AI 功能账户 ID，可选。")
    original_filename: str = Field(..., min_length=1, description="上传文件原始文件名。")
    content_type: str = Field(..., min_length=1, description="上传文件 MIME 类型。")
    file_size: int = Field(..., ge=0, description="上传文件大小，单位字节。")
    sha256: str | None = Field(None, min_length=1, description="上传文件 SHA-256 摘要，可选。")
    storage_path: str | None = Field(None, description="后端私有存储路径，可选，不建议前端依赖。")
    source_type: str = Field("script_docx", min_length=1, description="上传源类型。")
    extraction_status: str = Field("pending", min_length=1, description="文本提取状态。")
    extracted_text_length: int = Field(0, ge=0, description="已提取文本长度。")
    created_at: str | None = Field(None, description="上传源创建时间，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="上传源元数据扩展字段。")


class ScriptUploadOutput(BaseModel):
    source_id: str = Field(..., min_length=1, description="上传源唯一标识。")
    project_title: str = Field(..., min_length=1, description="项目标题。")
    extracted_text: str = Field(..., min_length=1, description="从上传剧本文档中提取出的文本。")
    metadata: UploadSourceMetadata = Field(..., description="上传源元数据。")
    warnings: list[str] = Field(default_factory=list, description="上传或解析过程中的非阻断警告。")

    @field_validator("extracted_text")
    @classmethod
    def validate_extracted_text(cls, value: str) -> str:
        stripped_value = value.strip()
        if stripped_value == "":
            raise ValueError("extracted_text 不能为空。")
        return stripped_value


class UploadError(BaseModel):
    error_code: str = Field(..., min_length=1, description="上传或解析错误码。")
    message: str = Field(..., min_length=1, description="面向调用方的错误信息。")
    detail: str | None = Field(None, description="错误详情，可选。")
    metadata: dict[str, Any] = Field(default_factory=dict, description="错误扩展元信息。")
