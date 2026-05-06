# Project / Session / Document Ownership Design｜项目、会话与文档归属设计

## 1. 背景与目标

Dramora 当前已经完成一批部署前基础能力：

- Internal Auth SQLite 持久化；
- `context_options` 已接入剧本生成、文档导入、文档导出；
- Usage Ledger 已持久化，并记录 user / workspace / project / session 等上下文；
- 生成、导入、导出链路已经能把安全摘要写入 Usage Ledger。

但 project / session / document 当前仍主要来自前端默认状态或请求上下文，还没有最小持久化归属表。多人内部使用时，如果没有项目、会话、文档归属事实来源，后续容易出现串项目、串上下文、导入文档误用于其他项目、导出记录难以追溯等问题。

第 352 步目标是设计 Project / Session / Document 最小持久化边界，为第 353～356 步落地准备：

- 防止多人内部使用时串项目、串上下文；
- 让生成、导入、导出、Usage Ledger 能绑定明确 project / session / document；
- 保持第一版足够轻量，服务公司内部 5～10 人稳定试用；
- 不做复杂多租户；
- 不做完整项目管理后台；
- 不做文件资产库；
- 不做云端部署。

## 2. 当前不解决的问题

本阶段暂不做：

- 完整项目管理后台；
- 复杂团队权限；
- 多租户商业隔离；
- 文件对象存储；
- 云端文件资产库；
- 完整版本管理系统；
- 多人协同编辑；
- 审批流；
- 生产级 RBAC；
- 跨项目知识库检索；
- 自动把历史项目内容拼入 LLM prompt。

Project / Session / Document 归属第一版只解决“这次操作属于谁、哪个 workspace、哪个 project、哪个 session、哪个 document”的最小事实记录，不解决完整企业项目管理系统。

## 3. 核心设计原则

- `user_id` 是操作者归属；
- `workspace_id` 是内部工作空间归属；
- `project_id` 是作品 / 项目归属；
- `session_id` 是一次创作 / 编辑会话归属；
- `document_id` 是导入 / 导出文档归属；
- `context_policy` 默认 `current_project_only`；
- LLM API Key 不是上下文隔离边界；
- Usage Ledger 只记录安全摘要，不负责权限判断；
- 任何跨项目读取必须显式授权和 UI 提示；
- 默认不跨项目拼接上下文；
- 默认不把历史项目内容隐式带入 LLM prompt。

## 4. Project 最小模型设计

建议新增 `projects` 表，第一版只记录项目归属和状态，不保存完整剧本文本。

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| `id` | text primary key | 项目 ID，对应 `ContextOptions.project_id`。 |
| `workspace_id` | text not null index | 项目所属 workspace。 |
| `owner_user_id` | text not null index | 项目创建者或主要负责人。 |
| `title` | text not null | 项目标题，可来自用户输入或生成结果标题。 |
| `source_mode` | text nullable | 初始来源，可为 `idea` / `film_script` / `novel`。 |
| `status` | text not null | 第一版可为 `active` / `archived`。 |
| `created_at` | text not null | 创建时间。 |
| `updated_at` | text not null | 更新时间。 |
| `last_active_at` | text nullable | 最近活跃时间。 |
| `metadata_json` | text nullable | 只存脱敏摘要。 |

设计说明：

- `source_mode` 可记录 `idea` / `film_script` / `novel`；
- `status` 可为 `active` / `archived`；
- `metadata_json` 只存脱敏摘要；
- 不存完整剧本文本；
- 不存完整上传文件；
- 不存 provider 原始响应；
- 不存 API Key、password、token、本机路径。

## 5. Session 最小模型设计

建议新增 `creative_sessions` 表，用于记录一次创作、编辑、导入、导出过程的会话归属。

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| `id` | text primary key | 会话 ID，对应 `ContextOptions.session_id`。 |
| `project_id` | text not null index | 所属 project。 |
| `workspace_id` | text not null index | 所属 workspace。 |
| `user_id` | text not null index | 会话发起或当前操作者。 |
| `source_mode` | text nullable | 当前会话入口，可为 `idea` / `film_script` / `novel`。 |
| `context_policy` | text not null | 默认 `current_project_only`。 |
| `status` | text not null | 第一版可为 `active` / `closed` / `archived`。 |
| `created_at` | text not null | 创建时间。 |
| `updated_at` | text not null | 更新时间。 |
| `last_event_at` | text nullable | 最近生成、导入、导出或编辑事件时间。 |
| `metadata_json` | text nullable | 只存脱敏摘要。 |

设计说明：

- 一个 project 可以有多个 session；
- session 记录一次创作 / 编辑 / 导出过程；
- `session_id` 进入 `ContextOptions`；
- 生成、导入、导出、Usage Ledger 都应绑定 `session_id`；
- 不把 session 当作长期聊天历史；
- 当前取消右侧 AI Assistant，不做聊天式 session 存储；
- 不存完整 prompt、完整剧本、完整上传文件或模型原始响应。

## 6. Document 最小模型设计

建议新增 `documents` 表，记录导入 / 导出文档的归属和安全摘要，不做文件资产库。

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| `id` | text primary key | 文档 ID。 |
| `project_id` | text not null index | 所属 project。 |
| `session_id` | text nullable index | 所属 session。 |
| `workspace_id` | text not null index | 所属 workspace。 |
| `user_id` | text not null index | 操作者。 |
| `document_type` | text not null | `source_script` / `short_drama_script` / `edited_script` 等。 |
| `source_stage` | text not null | `imported_document` / `generated_script` / `edited_script` / `export`。 |
| `direction` | text not null | `import` / `export`。 |
| `filename_safe` | text nullable | 安全清洗后的文件名。 |
| `content_type` | text nullable | MIME 类型摘要。 |
| `file_size_bytes` | integer nullable | 文件大小摘要。 |
| `character_count` | integer nullable | 文本字符数摘要。 |
| `export_format` | text nullable | `txt` / `json` / `docx`。 |
| `status` | text not null | `preview_ready` / `exported` / `failed` / `rejected`。 |
| `created_at` | text not null | 创建时间。 |
| `metadata_json` | text nullable | 只存脱敏 metadata。 |

设计说明：

- `direction` 可为 `import` / `export`；
- `document_type` 可为 `source_script` / `short_drama_script` / `edited_script`；
- `source_stage` 可为 `imported_document` / `generated_script` / `edited_script` / `export`；
- `filename_safe` 只保存安全清洗后的文件名，第一版可选；
- 不保存真实本机路径；
- 不保存完整 Word bytes；
- 不保存完整 `extracted_text`；
- 不保存完整导出文本；
- 文件资产管理不是当前阶段目标。

## 7. 与 ContextOptions 的关系

`ContextOptions` 是请求级上下文载体。Project / Session / Document 持久化后，`ContextOptions` 应尽量由后端真实记录生成或校验。

第一版关系：

- 当前前端默认 `context_options` 需逐步迁移；
- `context_options` 至少包含 `user_id` / `workspace_id` / `project_id` / `session_id` / `request_id` / `source_stage` / `context_policy`；
- `context_policy` 默认 `current_project_only`；
- 后端 service 应校验 `project_id` / `session_id` 是否属于当前 user / workspace；
- 如果缺少 project / session，开发期可创建或选择默认安全 project / session；
- 正式内部试运行前不应完全依赖硬编码默认值。

## 8. 与 Usage Ledger 的关系

Usage Ledger 记录 project / session / document 相关操作摘要，但不是项目表。

职责边界：

- Usage Ledger 记录 `project_id` / `session_id` / `document_operation`；
- Project / Session / Document repository 是归属事实来源；
- Usage Ledger 是操作日志，不是项目表；
- 生成、导入、导出写 ledger 时应复用真实 project / session / document 归属；
- ledger 不存完整正文；
- ledger 可用于审计“谁在什么项目做了什么”；
- ledger 查询后续必须按 user / workspace / project 过滤。

## 9. 与 Auth 的关系

Auth 是归属起点：

- 登录用户 `user_id` 是操作者归属；
- `workspace_id` 来自 Auth session；
- `safe_creator` 仍是开发期安全虚构账号；
- 正式内部试运行前需替换真实内部账号；
- 后续权限中间件可基于 `user_id` / `workspace_id` / `project_id` 做校验；
- 当前不做复杂 RBAC。

Project / Session / Document repository 不应自己实现密码、token 或登录逻辑。它只接收已经认证后的 user / workspace 上下文，并做归属校验。

## 10. 防串项目 guardrail

最小 guardrail 规则：

- 请求中的 `project_id` 必须属于当前 workspace；
- `session_id` 必须属于 `project_id`；
- `document_id` 必须属于 `project_id` / `session_id`；
- `context_policy=current_project_only` 时，不允许读取其他 project；
- 导入文档不能默认影响其他项目；
- 导出文档必须绑定当前 project / session；
- LLM prompt 构造时只能使用当前 project / session 的输入；
- 如果缺少 `project_id` / `session_id`，开发期可生成默认安全值，但正式内部试运行前应要求明确 project / session；
- 错误响应不泄露其他项目是否存在；
- Usage Ledger 记录 guardrail 拒绝时只能写安全错误码和脱敏摘要。

## 11. 前端迁移策略

当前前端已经有 `authContext`。当前 `context_options` 部分来自 auth response 和前端默认状态。

第 356 步迁移建议：

- 把前端 project / session context 从默认 mock 状态迁移到最小真实状态；
- 登录后自动创建或选择默认 project / session；
- 三入口生成、Word 导入、Document Export 都从当前 project / session 生成 `context_options`；
- 页面刷新是否保留状态可后续处理；
- 不在本阶段做复杂项目列表 UI；
- UI 不出现 mock / 后端 mock / 本地演示等用户可见开发文案；
- 缺少 project / session 时应给产品化提示，不暴露技术实现。

## 12. 后续步骤映射

- 第 353 步：project / session / document SQLite schema / repository；
- 第 354 步：生成、导入、导出绑定真实 project / session / document；
- 第 355 步：防串项目 guardrail 测试；
- 第 356 步：前端 project / session context 从默认状态迁移到最小真实状态。

每一步都应保持小闭环：repository 测试、service 测试、相关 endpoint / e2e 回归、敏感文件检查。

## 13. Go / No-Go 标准

完成 Project / Session / Document 归属后至少满足：

- repository 测试通过；
- 生成、导入、导出能绑定真实 project / session；
- Usage Ledger 能关联 project / session / document；
- 防串项目测试通过；
- 前端 `context_options` 不再完全依赖硬编码默认值；
- 不记录完整剧本文本；
- 不记录完整上传文件；
- 不提交数据库文件；
- git status clean；
- README / Roadmap 同步。

No-Go 条件：

- 需要提交真实数据库文件；
- 需要提交真实员工数据；
- 需要记录完整剧本文本或完整上传文件；
- 需要记录本机绝对路径；
- 需要将其他项目内容隐式拼入 LLM prompt；
- 需要把 API Key、password、token、`password_hash` 写入 project / session / document 表。
