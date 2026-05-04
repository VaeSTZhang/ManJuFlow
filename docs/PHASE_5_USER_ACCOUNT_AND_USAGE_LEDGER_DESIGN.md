# Phase 5 User Account and Usage Ledger Design｜公司用户账户与 AI 用量审计设计

> 当前状态：老板已取消当前版本的右侧 AI 聊天界面、AI Assistant、`/api/assistant/chat` 和 `suggested_actions`。本文中关于 Assistant Chat 的内容仅作为历史方案归档，不纳入当前实施路线。当前 UsageLedger 应优先覆盖三入口剧本生成 / 改编、在线编辑、导入导出、质量评审和后续分镜 / Prompt 工作流。

## 1. 设计目标

本设计用于未来公司人员扩张后，保证 ManJuFlow 能记录：

- 谁使用了系统；
- 在什么时候使用；
- 进行了哪类操作；
- 调用了哪个 AI 功能；
- 使用了哪个 provider / model；
- 输入和输出关联了哪个项目 / workspace；
- 结果是否成功；
- 消耗了多少 token / 资源；
- 折合人民币成本多少；
- 是否产生了可复用资产。

本步仍然是设计文档，不直接写账号系统，不直接接真实计费，不直接做权限系统，不新增数据库代码，也不接真实 DeepSeek。

## 2. 为什么需要公司内 AI 功能账户

公司后期人员会扩张，编剧、美术、导演、运营、制片等角色的使用方式不同。如果所有 AI 调用都记成同一个系统用户，后续会失去管理和审计能力。

需要公司内 AI 功能账户的原因：

- 每个人的聊天、上传、生成结果需要归属；
- 后期需要回溯创作责任链；
- 后期需要统计部门或个人资源消耗；
- 后期可能需要做权限、限额、报表、项目交接；
- 不同岗位需要不同功能入口和默认策略；
- 不应把所有 AI 调用都记成同一个系统用户；
- 员工不应直接持有真实 provider API Key。

## 3. 账号分层设计

建议至少分四层。

### CompanyUser

表示公司内部人员。

建议字段：

- `user_id`
- `display_name`
- `department`
- `role`
- `status`
- `created_at`
- `metadata`

说明：公开仓库只能放虚构字段和 mock 数据，不能放真实员工信息。

### AIWorkspaceAccount

表示员工在 ManJuFlow 内的 AI 功能账户。

建议字段：

- `ai_account_id`
- `user_id`
- `default_workspace_id`
- `enabled_features`
- `monthly_budget_limit`
- `usage_policy`
- `created_at`
- `status`
- `metadata`

说明：`AIWorkspaceAccount` 用于绑定聊天、上传、创作任务、资源消耗，不等同于 DeepSeek 真实账号。

### ProviderCredential / ModelProfile

表示底层模型供应商配置。

建议字段：

- `credential_id`
- `provider`
- `model`
- `purpose`
- `env_key_name`
- `status`
- `rate_limit_policy`
- `metadata`

说明：真实 API Key 只放在私有环境变量中，公开仓库只记录 `env_key_name` 占位，不写真实 key。

### UsageLedger

表示每次 AI 调用或资源消耗记录。

建议字段：

- `ledger_id`
- `user_id`
- `ai_account_id`
- `workspace_id`
- `project_title`
- `feature_name`
- `operation_type`
- `provider`
- `model`
- `request_id`
- `input_token_count`
- `output_token_count`
- `total_token_count`
- `unit_price`
- `currency`
- `estimated_cost`
- `estimated_cost_cny`
- `latency_ms`
- `status`
- `error_message`
- `created_at`
- `metadata`

## 4. 推荐的业务隔离策略

建议按业务链路隔离：

- Assistant Chat 是独立业务链路；
- Script / Storyboard / ImagePrompt 是内容生产链路；
- ImageGeneration 是渲染链路；
- 三者可以使用同一家 DeepSeek 或其他 provider，但必须在配置、prompt、service、usage ledger 中分开记录。

建议 `feature_name`：

- `assistant_chat`
- `idea_to_script`
- `script_to_storyboard`
- `storyboard_to_image_prompt`
- `script_segmentation`
- `image_generation_mock`
- `image_generation_comfyui_private`

建议 `operation_type`：

- `chat`
- `generate_script`
- `segment_script`
- `generate_storyboard`
- `generate_image_prompt`
- `generate_image`
- `export_json`
- `apply_suggested_action`

隔离原则：

- Assistant 不直接复用内容生产链路的 prompt；
- 内容生产链路不隐式读取 Assistant 对话；
- 用量记录必须能区分是聊天、改写、切分、分镜、Prompt 还是图片生成；
- 渲染链路即使是 mock，也可以先记录 mock usage，便于后续切换真实 provider。

## 5. DeepSeek 账号与 API Key 建议

用户希望聊天与内容生产分开，避免因为使用同一家 AI 导致项目运行混乱。

推荐策略：

- 最低要求：同一个 DeepSeek 账号下，创建不同 API Key；
- 更推荐：Assistant Chat 使用独立 DeepSeek API Key；
- 更高隔离：Assistant Chat 使用单独 DeepSeek 账号；
- 内容生产链路继续使用已有 provider 配置；
- 每个员工不直接持有真实 provider key；
- 每个员工持有 ManJuFlow 内部 `AIWorkspaceAccount`；
- 系统通过 `UsageLedger` 记录员工用量；
- 真实 provider key 由管理员在私有环境管理。

建议环境变量命名示例：

```env
DEEPSEEK_API_KEY
ASSISTANT_DEEPSEEK_API_KEY
ASSISTANT_LLM_PROVIDER
ASSISTANT_LLM_MODEL
ASSISTANT_REQUEST_TIMEOUT_SECONDS
```

说明：公开仓库只能写变量名，不能写真实 key、真实账号信息或真实账单。

## 6. 用量与人民币成本估算

未来应记录每次模型调用的 token 和成本估算。

建议记录：

- `input_token_count`
- `output_token_count`
- `total_token_count`
- `provider`
- `model`
- `unit_price`
- `currency`
- `estimated_cost`
- `fx_rate_to_cny`
- `estimated_cost_cny`
- `pricing_snapshot_at`
- `billing_note`

说明：

- MVP 早期可以使用 mock token / mock cost；
- LLM provider 返回 token usage 时优先使用 provider usage；
- provider 不返回 usage 时，可后续增加估算器；
- 价格表不应硬编码在业务逻辑里；
- 后续可建立 `ModelPricingProfile`；
- 汇率和价格会变化，正式版本要保存 `pricing_snapshot`，避免历史账单被新价格覆盖。

## 7. 聊天记录与 UsageLedger 的关系

每条 `AssistantMessage` 可以关联 `UsageLedger`。

建议关系：

- `AssistantConversation` 归属于 `ai_account_id` / `workspace_id`；
- `AssistantMessage` 记录用户和 AI 的对话；
- 每次 assistant 回复对应一条 `UsageLedger`；
- suggested action 的应用也可记录一条 `UsageLedger` 或 `ActionAudit`；
- 后续可以按人、项目、时间、模型查询用量。

示意：

```text
AssistantConversation
  -> AssistantMessage(user)
  -> AssistantMessage(assistant)
      -> UsageLedger(feature_name=assistant_chat)
      -> AssistantSuggestedActionRecord
```

## 8. 内容生产链路与 UsageLedger 的关系

以下操作都应该可以进入 `UsageLedger`：

- Idea → Script；
- Script → Storyboard；
- Storyboard → ImagePrompt；
- Existing Script → Script Segmentation；
- Assistant Chat；
- ImageGeneration；
- 导出 / 应用 suggested action 可选记录。

每次记录至少保留：

- `user_id` / `ai_account_id`；
- `workspace_id`；
- `feature_name`；
- `provider` / `model`；
- `request_id`；
- `status`；
- token / cost；
- `created_at`。

这样后续可以回答：

- 某个员工本月用了多少 AI；
- 某个项目消耗了多少成本；
- Assistant Chat 和内容生产分别花了多少；
- 哪些失败请求造成了成本浪费；
- 哪些生成结果产生了正式资产。

## 9. 权限、角色与部门预留

早期不做完整权限系统，但需要预留。

建议角色：

- `admin`
- `producer`
- `writer`
- `storyboard_artist`
- `prompt_designer`
- `reviewer`
- `viewer`

建议权限方向：

- `can_chat`
- `can_generate_script`
- `can_segment_script`
- `can_generate_storyboard`
- `can_generate_prompt`
- `can_generate_image`
- `can_export`
- `can_view_usage`
- `can_manage_users`
- `can_manage_provider_credentials`

说明：第五阶段早期可以只设计，不实现。后续进入公司私有部署时，再结合真实组织结构落地。

## 10. 本地开发与未来私有部署路线

### 阶段 A：公开仓库 mock

- 使用 mock `user_id`；
- 使用 mock `ai_account_id`；
- 使用 mock token / cost；
- 不保存真实员工和真实账单。

### 阶段 B：本地 SQLite

- 保存 users、ai_accounts、assistant_conversations、messages、usage_ledger；
- `storage/` 保存上传文件本体；
- 数据库文件不进入公开仓库。

### 阶段 C：公司私有部署

- 接入真实公司账号体系；
- 数据库迁移 PostgreSQL；
- 对接私有对象存储；
- 管理员配置 provider credentials；
- 生成用户用量报表；
- 支持人民币成本统计。

### 阶段 D：企业治理

- 角色权限；
- 审计日志；
- 预算限额；
- 部门报表；
- 项目归档；
- 离职账号冻结；
- 数据留存策略。

## 11. 公开仓库安全边界

公开仓库可以包含：

- 账号数据结构草案；
- `UsageLedger` 数据结构草案；
- mock user；
- mock ai_account；
- mock usage；
- 文档；
- 测试样例；
- `.env.example` 中的占位变量名。

公开仓库不能包含：

- 真实员工姓名；
- 真实员工账号；
- 真实聊天记录；
- 真实客户剧本；
- 真实账单；
- 真实 API Key；
- 真实 provider credential；
- 真实 token 用量；
- 真实人民币成本；
- 真实服务器地址；
- 生产数据库文件；
- `storage/` 文件本体。

## 12. 对第五阶段后续步骤的影响

由于新增账户与用量审计设计，后续第五阶段建议调整：

- 第 140 步：Phase 5 方案文档，已完成；
- 第 140.1 步：数据持久化与 Assistant 上下文设计，已完成；
- 第 140.2 步：用户账户与 UsageLedger 设计；
- 第 141 步：Script Segmentation Schema，但预留 `user_id` / `workspace_id` / `source_id`；
- 第 142 步：script segmentation mock service，返回 metadata；
- 第 143 步：`POST /api/scripts/segment`，可先不强制鉴权，但 mock `user_id`；
- 第 144 步：Script Segmentation 后端测试；
- 第 145 步：前端 ScriptSegmentation 类型和 API；
- 第 146 步：Sidebar 新增“已有剧本切分” workspace；
- 第 147 步：切分结果带入 Storyboard / ImagePrompt；
- 第 148 步：AI Assistant Panel 设计；
- 第 149 步：Assistant Chat Schema / mock service / endpoint，预留 `conversation_id`、`user_id`、`ai_account_id`、`usage_metadata`；
- 第 150 步：前端右侧 AssistantPanel mock UI；
- 第 151 步：Assistant suggested actions；
- 第 152 步：上传文件 API；
- 第 153 步：聊天记录本地持久化；
- 第 154 步：UsageLedger mock service；
- 第 155 步：阶段性浏览器验收。

## 13. 验收标准

第 140.2 步验收标准：

- `docs/PHASE_5_USER_ACCOUNT_AND_USAGE_LEDGER_DESIGN.md` 已新增；
- 文档明确每个员工应拥有公司内 AI 功能账户；
- 文档明确 `AIWorkspaceAccount` 与 provider API Key 不等同；
- 文档明确 Assistant Chat 与内容生产链路分开统计；
- 文档明确 `UsageLedger` 字段草案；
- 文档明确 token、模型、人民币成本估算字段；
- 文档明确 DeepSeek API Key 隔离建议；
- 文档明确聊天记录与 `UsageLedger` 的关系；
- 文档明确公开仓库安全边界；
- 不修改代码；
- 不引入真实员工、真实 key、真实账单或真实客户数据。
