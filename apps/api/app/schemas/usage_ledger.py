from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.context import ContextOptions


UsageLedgerStatus = Literal["success", "failed", "blocked", "skipped"]
UsageLedgerOperation = Literal[
    "script_generation",
    "film_adaptation",
    "novel_adaptation",
    "document_import",
    "document_export",
    "quality_review",
]
UsageLedgerMetadataValue = str | int | float | bool | None


class UsageLedgerCostEstimate(BaseModel):
    input_tokens: int | None = Field(None, ge=0, description="输入 token 数，可选。")
    output_tokens: int | None = Field(None, ge=0, description="输出 token 数，可选。")
    total_tokens: int | None = Field(None, ge=0, description="总 token 数，可选。")
    estimated_cost_cny: float | None = Field(None, ge=0, description="人民币成本估算，可选。")
    currency: str = Field("CNY", min_length=1, description="成本估算币种，默认 CNY。")


class UsageLedgerCreate(BaseModel):
    operation: UsageLedgerOperation = Field(..., description="本次用量记录对应的业务操作。")
    status: UsageLedgerStatus = Field(..., description="本次操作状态。")
    context: ContextOptions | None = Field(None, description="本次操作归属的上下文，可选。")
    provider: str | None = Field(None, description="模型 provider，可选。")
    model: str | None = Field(None, description="模型名称，可选。")
    purpose: str | None = Field(None, description="AI 请求用途，可选。")
    source_mode: str | None = Field(None, description="来源入口，可选。")
    source_stage: str | None = Field(None, description="内容阶段，可选。")
    prompt_template_name: str | None = Field(None, description="Prompt 模板名称，可选。")
    request_id: str | None = Field(None, description="请求追踪 ID，可选。")
    duration_ms: int | None = Field(None, ge=0, description="耗时，单位毫秒，可选。")
    cost_estimate: UsageLedgerCostEstimate | None = Field(None, description="成本估算，可选。")
    error_code: str | None = Field(None, description="错误码，可选。")
    error_message: str | None = Field(None, description="错误摘要，可选，不应包含完整剧本或 provider 原始响应。")
    metadata: dict[str, UsageLedgerMetadataValue] = Field(
        default_factory=dict,
        description="扩展元信息，不应包含剧本文本、provider 原始响应或 API Key。",
    )


class UsageLedgerEntry(UsageLedgerCreate):
    ledger_id: str = Field(..., min_length=1, description="用量记录 ID。")
    started_at: str | None = Field(None, description="操作开始时间，可选。")
    finished_at: str | None = Field(None, description="操作结束时间，可选。")


class UsageLedgerSummary(BaseModel):
    total_entries: int = Field(..., ge=0, description="用量记录总数。")
    success_count: int = Field(..., ge=0, description="成功记录数。")
    failed_count: int = Field(..., ge=0, description="失败记录数。")
    blocked_count: int = Field(..., ge=0, description="阻断记录数。")
    estimated_total_cost_cny: float = Field(0.0, ge=0, description="人民币总成本估算。")
    currency: str = Field("CNY", min_length=1, description="汇总币种。")
