from typing import Literal

from pydantic import BaseModel, Field, field_validator


DocumentImportActionType = Literal["fill", "append", "cancel"]
DocumentImportStatus = Literal["preview_ready", "failed", "rejected"]
DocumentImportMetadataValue = str | int | float | bool | None


class DocumentImportSource(BaseModel):
    filename: str = Field(..., min_length=1, description="导入文件原始文件名。")
    content_type: str | None = Field(None, description="导入文件 MIME 类型，可选。")
    file_size_bytes: int | None = Field(None, ge=0, description="导入文件大小，单位字节，可选。")
    source_type: str = Field("docx", min_length=1, description="导入源类型，第一版默认 docx。")
    checksum: str | None = Field(None, min_length=1, description="文件摘要，可选。")

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        stripped_value = value.strip()
        if stripped_value == "":
            raise ValueError("filename 不能为空。")
        return stripped_value


class DocumentImportPreviewRequest(BaseModel):
    filename: str = Field(..., min_length=1, description="待预览导入文件名。")
    extracted_text: str = Field(
        ...,
        min_length=1,
        description="已提取的文档文本，用于 JSON preview endpoint；不代表最终 multipart 上传接口。",
    )
    content_type: str | None = Field(None, description="导入文件 MIME 类型，可选。")
    file_size_bytes: int | None = Field(None, ge=0, description="导入文件大小，单位字节，可选。")
    source_type: str = Field("docx", min_length=1, description="导入源类型，第一版默认 docx。")
    project_title: str | None = Field(None, description="项目标题，可选。")
    checksum: str | None = Field(None, min_length=1, description="文件摘要，可选。")

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        stripped_value = value.strip()
        if stripped_value == "":
            raise ValueError("filename 不能为空。")
        return stripped_value

    @field_validator("extracted_text")
    @classmethod
    def validate_extracted_text(cls, value: str) -> str:
        stripped_value = value.strip()
        if stripped_value == "":
            raise ValueError("extracted_text 不能为空。")
        return value


class DocumentImportPreview(BaseModel):
    source: DocumentImportSource = Field(..., description="导入文件基础元信息。")
    extracted_text: str = Field(..., min_length=1, description="从文档中提取的完整文本。")
    preview_text: str = Field(..., min_length=1, description="用于前端预览的文本片段。")
    character_count: int = Field(..., ge=0, description="提取文本字符数。")
    paragraph_count: int | None = Field(None, ge=0, description="段落数量，可选。")
    detected_title: str | None = Field(None, description="从文档中识别到的标题，可选。")
    warnings: list[str] = Field(default_factory=list, description="导入过程中的非阻断警告。")
    metadata: dict[str, DocumentImportMetadataValue] = Field(
        default_factory=dict,
        description="导入预览扩展元信息，不应包含本机绝对路径或敏感内容。",
    )


class DocumentImportAction(BaseModel):
    action: DocumentImportActionType = Field(..., description="用户确认导入预览后的动作。")
    target_field: str = Field("source_text", min_length=1, description="前端目标字段，默认 source_text。")
    imported_text: str | None = Field(None, description="用户确认填入或追加后的导入文本，可选。")


class DocumentImportOutput(BaseModel):
    project_title: str | None = Field(None, description="项目标题，可选。")
    status: DocumentImportStatus = Field("preview_ready", description="导入状态。")
    preview: DocumentImportPreview = Field(..., description="导入预览。")
    next_required_action: str = Field(
        "user_confirm_import_action",
        min_length=1,
        description="下一步需要用户确认填入、追加或取消，并继续填写改编方向。",
    )


class DocumentImportError(BaseModel):
    error_code: str = Field(..., min_length=1, description="文档导入错误码。")
    message: str = Field(..., min_length=1, description="面向调用方的错误信息。")
    filename: str | None = Field(None, description="导入文件名，可选。")
    details: dict[str, DocumentImportMetadataValue] = Field(
        default_factory=dict,
        description="错误扩展信息，不应包含本机绝对路径、敏感内容或完整文件内容。",
    )
