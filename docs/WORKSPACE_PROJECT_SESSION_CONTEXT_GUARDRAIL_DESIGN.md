# Workspace / Project / Session Context Guardrail Design｜上下文隔离护栏设计

## 1. 背景与风险

Dramora 短中期目标是公司内部 5～10 人长期稳定使用。多个内部用户可以共用同一个后端服务，也可以共用同一个底层 LLM API Key，但同一个 API Key 只是 provider 认证与计费凭证，不应该被当作业务上下文边界。

真正的隔离边界应来自：

- `user_id`
- `workspace_id`
- `project_id`
- `session_id`

如果没有清晰上下文隔离，后续会出现高风险问题：

- A 项目的剧本被带入 B 项目；
- 电影剧本改编上下文串到小说 / 网文改编；
- 上传文件被错误读取或复用；
- 编辑稿和 AI 原始稿归属混乱；
- 导出文件拿到错误项目的 `effectiveScript`；
- 用量记录无法归属到正确员工、项目或会话；
- 如果未来恢复 Assistant / 历史记录 / RAG，可能引用错误历史。

当前版本取消的是右侧聊天式 AI Assistant，不取消核心 LLM 创作能力。三入口剧本生成、电影剧本改编、小说 / 网文改编、质量评审和后续分镜 / Prompt 工作流都必须在明确上下文边界内运行。

## 2. 当前已有保护

当前已有初步保护：

- LLM 调用是 request-level；
- 生成结果 metadata 已出现 `context_policy = current_project_only`；
- `AIRequestOptions` 已记录 provider / model / purpose；
- 当前版本未启用右侧 AI Assistant；
- 当前未启用长期记忆 / RAG / 全局历史检索；
- 公开仓库不保存真实客户数据；
- `.env` 不提交；
- 真实 API Key 只存在本地或私有部署环境。

这些保护降低了短期串上下文风险，但不等于完整隔离。当前仍缺少统一的上下文契约、权限校验、项目 / 会话级状态隔离、文件归属和用量归属。

## 3. 必须新增的上下文标识

后续所有生成、导入、导出、质量评审、用量记录和文件处理链路都应逐步统一以下字段。

### user_id

内部员工或账号归属。

用途：

- 标识谁发起操作；
- 绑定内部账号、用量、权限和审计；
- 避免把所有 AI 调用都记到系统默认用户。

### workspace_id

公司内部工作区或项目组归属。

用途：

- 区分不同团队、部门、项目组或工作台；
- 用于控制上传文件、生成记录和导出资产的可见范围；
- 支撑未来内部多项目并发使用。

### project_id

单个剧本项目归属。

用途：

- 绑定三入口生成、在线编辑、导入文档和导出文件；
- 防止 A 项目的 `source_text`、`generatedScript`、`editableScript` 被 B 项目复用；
- 作为历史读取和质量评审的默认过滤条件。

### session_id

一次创作 / 编辑会话归属。

用途：

- 绑定一次从输入、生成、编辑到导出的工作流；
- 防止同一项目下多个并行编辑会话互相覆盖；
- 支撑返回上一阶段时恢复正确状态。

### request_id

一次 API 调用追踪。

用途：

- 关联日志、错误、用量记录和 provider 调用；
- 便于定位超时、schema 错误、contract failure；
- 不承载剧本文本或敏感内容。

### source_mode

当前创作入口或来源类型。

建议取值：

- `idea`
- `film_script`
- `novel`
- `uploaded_document`
- `assistant_rewrite`

用途：

- 区分灵感生成、电影改编、小说改编和上传文档；
- 决定 prompt、schema、质量验收和导出说明；
- 防止不同入口上下文混用。

### source_stage

当前内容阶段。

建议取值：

- `draft`
- `generated_script`
- `edited_script`
- `imported_document`
- `export`
- `quality_review`
- `storyboard`
- `prompt`

用途：

- 标识内容处于草稿、生成结果、编辑稿、导入文档还是导出阶段；
- 确保后续工作流读取的是正确阶段的 payload；
- 便于 UsageLedger 和质量评审分类。

### context_policy

上下文读取策略。

建议取值：

- `current_project_only`
- `current_session_only`
- `no_cross_project_context`

用途：

- 明确 prompt 构造和历史读取边界；
- 默认禁止跨项目上下文；
- 如果未来允许跨项目参考，必须显式授权并在 UI 中提示。

## 4. 后端 guardrail 原则

后端应遵守以下原则：

- 所有生成、导入、导出、质量评审、用量记录接口后续都应接收或生成 context ids；
- 所有 service 禁止从全局变量读取上一次请求内容；
- 所有历史读取必须带 `project_id` / `session_id` 过滤；
- 没有明确 project / session 归属的内容不得进入 LLM prompt；
- 上传文件解析结果必须绑定 `project_id` / `session_id`；
- 导出文件必须来源于当前 project / session 的 `effectiveScript`；
- UsageLedger 必须记录 context ids；
- contract failure、schema failure、provider failure 等错误不应记录完整剧本文本；
- 错误日志不记录完整剧本原文；
- provider 原始响应不直接入公开日志；
- API Key、`.env`、本机绝对路径不得进入 metadata 或错误响应；
- assistant_rewrite / uploaded_document 等未来入口不得绕开上下文校验。

推荐做法：

- 在 schema 层逐步显式化 context ids；
- 在 service 层接收上下文对象或上下文字段；
- 在 router 层做基础归属校验；
- 在 metadata 中只记录轻量追踪字段；
- 在测试中验证错误响应不包含 `source_text`、完整输出或本机路径。

## 5. 前端 guardrail 原则

前端不能只依赖全局 `selectedScript` / `generatedScript`。

后续应确保以下状态归属于当前 project / session：

- 三入口草稿；
- 文档导入预览；
- 生成结果 `generatedScript`；
- 编辑稿 `editableScript`；
- 当前有效稿 `effectiveScript`；
- 导出 loading / error 状态；
- 质量评审结果；
- 后续分镜 / Prompt payload。

前端行为原则：

- 切换项目时不能复用上一个项目的 `source_text` / `generatedScript`；
- film_script 和 novel 的导入预览状态必须继续隔离；
- 进入 Prompt / 分镜下一阶段时应显式携带 `project_id` / `session_id`；
- 返回上一阶段时只恢复当前 project / session 的状态；
- 导出应使用当前 project / session 的 `effectiveScript`；
- 未来 Assistant suggested_actions 必须由用户确认，不得自动覆盖编辑内容；
- 前端 UI 不出现 mock / 后端 mock / 本地演示等用户可见开发文案。

## 6. LLM Prompt 构造 guardrail

Prompt messages 只能包含当前 request payload 和当前 project / session 允许的上下文。

必须遵守：

- 不允许拼接全局历史；
- 不允许跨 workspace 检索；
- 不允许把其他项目的上传文件、生成结果或编辑稿塞进 prompt；
- 不允许把所有历史聊天或历史生成记录无脑塞进 prompt；
- Assistant 后续如果恢复，也只能读取 `current_project_only`；
- 如果需要跨项目参考，必须显式授权和 UI 提示；
- prompt metadata 必须记录 `context_policy`；
- provider / model 选择通过 `AIRequestOptions` 管理，不代表上下文边界；
- prompt 中不包含 API Key、`.env`、本机路径或真实客户敏感信息。

默认策略：

```text
context_policy = current_project_only
allow_cross_project_context = false
```

如果后续引入 RAG / 历史记录 / 搜索能力，检索 query 必须强制带 `workspace_id` / `project_id` / `session_id` 过滤条件。

## 7. 数据持久化 guardrail

后续数据库落地时，以下表都必须包含上下文字段：

- `scripts`
- `documents`
- `exports`
- `usage_ledger`
- `quality_reviews`
- `projects`
- `workspaces`
- `sessions`

基础字段建议：

- `user_id`
- `workspace_id`
- `project_id`
- `session_id`
- `request_id`
- `source_mode`
- `source_stage`
- `context_policy`
- `created_at`
- `updated_at`
- `metadata`

查询原则：

- 普通业务查询默认按 `project_id` / `workspace_id` 过滤；
- 用户只能访问授权 workspace / project；
- 管理员视角另行设计，不能混进普通业务 service；
- 上传文件、导出文件和质量评审必须可追溯到 project / session；
- 不在公开仓库提交真实数据库文件；
- 本地 SQLite 只用于开发或安全样例；
- 真实员工信息、真实客户剧本、真实上传文件只进入私有部署环境。

## 8. 测试策略

后续必须补充以下测试：

- project A 输入不会出现在 project B metadata；
- session A 的 uploaded document 不会被 session B 使用；
- `generate-from-source` 会回传 `project_id` / `session_id`；
- document import 绑定 project / session；
- document export 绑定 project / session；
- UsageLedger 记录 context ids；
- 质量评审记录 context ids；
- Assistant 后续如恢复，不读取跨项目历史；
- 没有 context id 时使用安全默认或返回清晰错误，具体按阶段决定；
- 错误响应不包含 `source_text`、完整剧本、provider 原始响应、API Key、本机路径；
- 前端切换项目后不会保留上一个项目的草稿、导入预览、生成结果或编辑稿。

测试样本必须使用安全虚构内容，不使用真实客户剧本、真实电影剧本或真实小说原文。

## 9. 分阶段落地路线

建议路线：

- 第 301 步：新增上下文隔离护栏设计文档；
- 第 302 步：为 `ShortDramaGenerationInput` / `AIRequestOptions` 或独立 `ContextOptions` 预留 `workspace_id` / `project_id` / `session_id` / `user_id`；
- 第 303 步：metadata 回传 context ids 并补测试；
- 第 304 步：document import / export schema 接入 context ids；
- 第 305 步：usage ledger schema 接入 context ids；
- 第 306 步：前端 `CreationHome` 状态按 project / session 归属整理；
- 第 307 步：e2e 覆盖切换项目不串状态；
- 第 308 步：部署前安全检查更新。

实施要求：

- 每步保持小改动；
- 每步有对应测试或文档验收；
- 不一次性引入复杂权限系统；
- 不为了上下文隔离重写整个前后端；
- 不恢复当前版本已取消的右侧聊天式 Assistant。

## 10. 当前非目标

本阶段不做：

- 真实账号系统；
- 权限数据库；
- 复杂多租户 SaaS；
- 跨公司隔离；
- 真实审计后台；
- 右侧 Assistant 恢复；
- Redis；
- Celery；
- RAG；
- 向量数据库；
- 跨项目自动检索；
- 真实员工账号数据；
- 真实客户数据持久化。

当前重点是为内部 5～10 人稳定使用建立清晰边界，确保后续代码不会把上下文、文件、导出和用量记录写散。

## 11. 验收标准

本设计文档通过标准：

- 明确同一 LLM API Key 不等于同一上下文；
- 明确 user / workspace / project / session 边界；
- 明确后端 guardrail；
- 明确前端 guardrail；
- 明确 Prompt 构造 guardrail；
- 明确数据持久化 guardrail；
- 明确后续测试策略；
- 明确分阶段落地步骤；
- 明确当前非目标；
- 不包含真实敏感数据；
- 不改代码。

当前结论：

Dramora 可以共用同一个后端和同一个 LLM provider key，但每次生成、导入、导出、质量评审和用量记录都必须逐步绑定清晰的 user / workspace / project / session 上下文。上下文隔离应先以轻量 schema / metadata / 测试 guardrail 落地，再进入账号、用量和持久化实现。
