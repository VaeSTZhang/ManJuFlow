# Usage Ledger Persistence SQLite Design｜用量记录持久化 SQLite 设计

## 1. 背景与目标

当前 Usage Ledger 第一版已经完成：

- schema / service / 生成链路 metadata；
- 可记录 `operation`、`provider`、`model`、`purpose`、`status`、`request_id`、`context`；
- 生成链路已能把安全的 `usage_ledger` 摘要写入 `ShortDramaScriptOutput.metadata`；
- SQLite repository 已完成；
- 剧本生成、文档导入预览、TXT / JSON / DOCX 导出链路已写入 SQLite Usage Ledger；
- 明确不记录完整剧本文本、完整上传文件、完整 provider 原始响应、API Key、密码、token、本机路径；
- 第 351 步补充脱敏安全测试与文档状态同步。

第 347 步目标是设计 SQLite 最小持久化方案，为第 348～351 步落地做准备。当前第 348～350 步已完成 repository 与核心写入链路，第 351 步用于阶段收口。

本方案服务 Dramora 短中期公司内部 5～10 人长期稳定使用，不做复杂财务系统、不做精确云账单对账、不做多租户商业计费系统。

## 2. 当前不解决的问题

本阶段暂不做：

- 精确模型账单对账；
- 自动人民币扣费；
- 多租户商业计费；
- 支付系统；
- 发票系统；
- 复杂 BI 看板；
- Redis / Celery 异步队列；
- 外部日志平台；
- 真实客户内容审计；
- provider 原始响应长期归档；
- 用量记录管理后台；
- Usage Ledger 查询页面；
- 管理员审计后台；
- 公开商用计费体系。

Usage Ledger 第一版的目标是内部归属、成本线索和问题排查，不是财务结算系统。

## 3. SQLite 最小落地边界

SQLite 作为内部试运行阶段的用量记录持久化方案：

- 适合 5～10 人内部使用；
- 单机部署简单；
- 易备份；
- 后续可迁移 PostgreSQL；
- 比非持久化 service 更接近真实内部使用；
- 数据库文件必须进入 `.gitignore`；
- 数据库文件不能提交公开仓库。

Usage Ledger 可以与 Auth SQLite 共用同一个数据库文件，也可以拆分为单独数据库文件。第 348 步落地时再根据 repository 初始化和备份策略决定。无论采用哪种方式，数据库文件都不能放入 git。

## 4. `usage_ledger` 表设计初稿

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| `id` | text primary key | 用量记录主键，可使用 `usage_<request_id>` 或 uuid-like string。 |
| `request_id` | text nullable index | 一次 API 调用追踪 ID。 |
| `user_id` | text nullable index | 来自 `context_options` 或 auth session。 |
| `username` | text nullable | 安全用户名摘要，不存真实隐私扩展字段。 |
| `workspace_id` | text nullable index | 工作区归属。 |
| `project_id` | text nullable index | 项目归属。 |
| `session_id` | text nullable index | 创作 / 编辑会话归属。 |
| `context_policy` | text not null default `current_project_only` | 上下文隔离策略。 |
| `operation` | text not null | `script_generation` / `document_import` / `document_export` / `quality_review` 等。 |
| `purpose` | text nullable | AI 请求用途，例如 `script_generation`。 |
| `provider` | text nullable | 模型 provider。 |
| `model` | text nullable | 模型名称。 |
| `generation_mode` | text nullable | `mock` / `llm` 等生成模式。 |
| `status` | text not null | `success` / `failed` / `rejected` / `skipped`。 |
| `source_mode` | text nullable | `idea` / `film_script` / `novel` 等入口。 |
| `document_operation` | text nullable | `import_preview` / `export_txt` / `export_json` / `export_docx` 等。 |
| `input_character_count` | integer nullable | 输入字符数摘要。 |
| `output_character_count` | integer nullable | 输出字符数摘要。 |
| `prompt_token_count` | integer nullable | prompt token 数。 |
| `completion_token_count` | integer nullable | completion token 数。 |
| `total_token_count` | integer nullable | token 总数。 |
| `estimated_cost_cny` | real nullable | 人民币成本估算。 |
| `latency_ms` | integer nullable | 请求耗时。 |
| `error_code` | text nullable | 安全错误码。 |
| `error_message_safe` | text nullable | 脱敏错误摘要。 |
| `created_at` | text not null | 记录创建时间。 |
| `metadata_json` | text nullable | 只存脱敏 metadata JSON。 |

设计说明：

- `id` 为主键；
- `request_id` 便于串联一次请求；
- `user_id` / `workspace_id` / `project_id` / `session_id` 来自 `context_options`；
- `operation` 覆盖 script generation、document import、document export、quality review；
- `status` 可为 `success` / `failed` / `rejected` / `skipped`；
- `error_message_safe` 只能存安全摘要；
- `metadata_json` 只能存脱敏 metadata；
- 不存完整剧本；
- 不存完整上传文件；
- 不存完整 provider response；
- 不存 API Key / token / password。

## 5. 安全字段边界

允许记录：

- `user_id`；
- `username`；
- `workspace_id`；
- `project_id`；
- `session_id`；
- `request_id`；
- `provider`；
- `model`；
- `purpose`；
- `operation`；
- `source_mode`；
- `status`；
- token 数；
- 字符数；
- `estimated_cost_cny`；
- 安全 `error_code`；
- 脱敏 `error_message_safe`。

禁止记录：

- 完整 `source_text`；
- 完整 generated script；
- 完整 Word 文件内容；
- 完整 `extracted_text`；
- provider 原始响应；
- API Key；
- password；
- `password_hash`；
- `access_token`；
- session token；
- 本机绝对路径；
- 真实服务器地址；
- 合作方敏感资料。

## 6. 与 Auth / ContextOptions 的关系

Usage Ledger 必须绑定 Auth 登录返回的 user / session / workspace / context policy：

- 同一个 LLM API Key 不是用户隔离边界；
- `user_id` / `workspace_id` / `project_id` / `session_id` 是归属基础；
- `context_policy` 默认 `current_project_only`；
- `request_id` 用于追踪一次生成、导入、导出或质量评审请求；
- 若用户未登录，开发期可落到 `safe_creator` 或 `anonymous_internal`，但正式内部试运行应要求登录。

Usage Ledger 不负责权限判断。权限边界应由 Auth / ContextOptions / service guardrail 处理，Usage Ledger 只记录安全摘要。

## 7. 与剧本生成链路的关系

第 349 步已接入：

- `idea` / `film_script` / `novel` 三入口生成写入 usage ledger；
- 记录 `provider` / `model` / `purpose` / `source_mode` / `generation_mode`；
- 记录 `target_episode_count`、`episode_count`、`characters_count` 等非敏感结构化摘要可选；
- 不记录完整输入原文；
- 不记录完整模型输出；
- 生成失败也要记录 `failed` 状态和安全错误码；
- contract guardrail 失败可以记录 `rejected` 或 `failed`，但只存安全原因摘要。

当前生成链路已能持久化安全摘要，并继续把脱敏 `usage_ledger` 摘要写入 metadata。后续查询 UI 或审计后台应复用 repository，不应重新记录完整文本。

## 8. 与文档导入 / 导出的关系

第 350 步已接入：

- document import preview 写 usage ledger；
- document export TXT / JSON / DOCX 写 usage ledger；
- 记录 `file_size_bytes` / `character_count` / `export_format` / `source_stage` 等安全摘要；
- 不记录完整上传文件；
- 不记录完整 `extracted_text`；
- 不记录导出文件 bytes；
- 不记录本机路径；
- 失败时记录安全错误码和脱敏错误摘要。

Document Import / Export 已经支持 `context_options`，当前写入链路直接复用这些上下文字段，不在导入 / 导出 service 中重新发明 user / project 字段。

## 9. 成本估算策略

第一版可以存 `estimated_cost_cny`：

- 如果 provider 返回 token usage，可基于 token 数估算；
- 如果没有 token usage，可基于字符数粗略估算或留空；
- 成本字段用于内部观察，不作为财务结算；
- 价格表不写死到业务逻辑中，后续可单独配置；
- 不在公开仓库写真实采购折扣或商业敏感价格；
- 汇总时可按 provider / model / user / project / operation 维度统计。

成本估算必须标记为 estimate，不应在 UI 或文档中暗示已经完成真实账单对账。

## 10. Repository 设计

后续可新增：

```text
apps/api/app/repositories/usage_ledger_repository.py
```

建议方法：

- `init_schema()`；
- `create_entry(entry)`；
- `list_entries(limit=100, user_id=None, workspace_id=None, project_id=None)`；
- `get_entry_by_request_id(request_id)`；
- `summarize_by_user(...)`；
- `summarize_by_provider(...)`；
- `summarize_by_operation(...)`。

职责边界：

- repository 负责 SQLite 读写；
- service 负责脱敏、归一化、成本估算；
- router 后续可以先不暴露管理查询接口，避免过早做后台；
- 查询默认应按 `workspace_id` / `project_id` / `user_id` 过滤；
- 管理员聚合视角后续单独设计。

## 11. Service 迁移策略

当前 `usage_ledger_service` 可保留对外函数：

- `create_usage_ledger_entry(...)`；
- `summarize_usage_ledger(...)`。

迁移策略：

- 先写 repository 测试；
- 再让 service 支持可注入 repository；
- 底层从内存记录切到 repository；
- 现有调用方尽量不大改；
- 不把 Usage Ledger 查询 UI 作为当前前置；
- 先保证写入可追溯；
- 保持 dangerous metadata key 过滤；
- 不把完整文本、原始响应或 secret 写入 `metadata_json`。

如果持久化写入失败，第一版可选择让主业务请求继续返回并记录安全错误日志，或返回明确错误。具体策略应在第 349 / 350 步按业务风险决定。

## 12. 日志脱敏与错误响应

记录失败时必须遵守：

- 不写完整异常堆栈到 usage ledger；
- 不写 provider 原始错误全文；
- 只写安全 `error_code` / `error_message_safe`；
- 不写本机路径；
- 不写 API Key；
- 不写 token；
- 不写密码；
- 不写完整文本。

错误摘要应帮助内部排查，例如：

- `provider_timeout`；
- `script_generation_contract_failed`；
- `document_import_parse_failed`；
- `document_export_failed`。

错误摘要不应包含用户上传的正文、完整 prompt、完整模型输出或数据库路径。

## 13. 后续步骤映射

当前小步状态：

- 第 348 步：usage_ledger SQLite schema / repository，已完成；
- 第 349 步：剧本生成链路写入 usage ledger，已完成；
- 第 350 步：文档导入 / 导出链路写入 usage ledger，已完成；
- 第 351 步：用量记录脱敏测试 + 文档同步，当前阶段收口。

后续增强：

- Usage Ledger 查询页面；
- 管理员审计视图；
- 精确 token / 成本对账；
- 与正式权限中间件结合的查询过滤。

每一步都应保持小闭环：repository 测试、service 测试、相关 endpoint / e2e 回归、敏感文件检查。

## 14. Go / No-Go 标准

完成 Usage Ledger 持久化后至少要满足：

- repository 测试通过；
- service 测试通过；
- 剧本生成写入 usage ledger；
- 文档导入 / 导出写入 usage ledger；
- 失败请求也能安全记录；
- 脱敏测试覆盖 script generation / document import / document export / failed ledger；
- 不记录完整剧本文本；
- 不记录完整上传文件；
- 不记录 provider 原始响应；
- 不记录 API Key / password / token；
- 数据库文件不进入 git；
- git status clean；
- README / Roadmap 同步。

No-Go 条件：

- 需要提交真实数据库文件；
- 需要提交真实员工数据或真实账单数据；
- 需要记录完整剧本文本；
- 需要记录完整上传文件；
- 需要记录 provider 原始响应；
- 需要把 API Key、password、token、`password_hash` 写入 ledger；
- 测试依赖真实客户内容或真实 provider 响应。
