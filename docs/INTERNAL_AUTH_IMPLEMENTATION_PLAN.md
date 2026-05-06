# Internal Auth Implementation Plan｜内部账号与权限落地方案

## 1. 背景

Dramora 当前面向公司内部 5～10 人长期稳定使用，不以公开商用 SaaS、多公司多租户或公开注册为当前目标。

当前前端存在 mock login 和 mock context：

- `user_id = internal_user_mock_001`
- `workspace_id = workspace_dramora_internal`
- `project_id = project_creation_default`
- `session_id = session_creation_default`

这些字段只是开发期占位，用于验证三入口剧本生成、Document Import / Export、Usage Ledger 和上下文隔离链路。它们不等于正式内部账号系统，也不等于正式权限系统。

上云或进入公司内部长期使用前，Dramora 至少需要第一版内部账号、登录态和权限边界，确保生成、导入、导出、用量记录和质量评审都能归属到明确用户、工作区、项目和会话。

## 2. 当前已有基础

当前已经具备：

- `ContextOptions` 后端 schema；
- 前端三入口请求携带 `context_options`；
- Document Import / Export 请求携带 `context_options`；
- Usage Ledger schema / service 第一版；
- 剧本生成链路 metadata 附带 `usage_ledger`；
- `.gitignore` 已覆盖 `.env`、本地产物、上传目录、构建产物和测试报告；
- 真实 API Key 只应放本地或私有部署环境。

当前尚未具备：

- 正式用户表；
- 正式登录接口；
- 密码哈希；
- 权限校验；
- session token 或 JWT；
- 用户 / 项目 / 文档 / 用量记录持久化；
- 管理员账号管理界面。

## 3. 内部账号第一版目标

第一版目标用户：

- 公司内部 5～10 人；
- 编剧；
- 运营；
- 内容负责人；
- 管理员。

第一版账号字段建议：

- `user_id`
- `username`
- `display_name`
- `password_hash`
- `role`
- `status`
- `created_at`
- `updated_at`

`username` 必须支持中文和英文，方便内部员工用姓名、英文名或内部约定账号登录。

密码规则第一版建议：

- 用户自设密码必须包含大写字母；
- 必须包含小写字母；
- 必须包含数字；
- 后续再评估特殊字符、最小长度、管理员邀请、首次登录强制改密和密码过期策略。

角色建议：

- `admin`：账号管理、配置管理、用量查看；
- `creator`：剧本生成、改编、导入、编辑、导出；
- `reviewer`：查看项目、质量评审、导出；
- `viewer`：只读查看和下载。

账号状态建议：

- `active`
- `disabled`
- `pending`

## 4. 第一版不做什么

第一版不做：

- 手机号实名；
- 短信验证码；
- OAuth；
- 企业微信 / 飞书登录；
- 复杂 RBAC；
- 多公司多租户；
- 公开注册；
- 支付系统；
- 公开商用用户体系；
- 多端设备管理；
- 复杂审计后台；
- 管理员自助重置密码完整闭环。

这些能力可以在真实内部试用后按需求评估，不应成为当前部署前的复杂前置项。

## 5. 推荐技术路线

后端建议：

- 新增 FastAPI auth router；
- 开发期使用 SQLite 用户表；
- 后续私有服务器可迁移到 Postgres；
- `password_hash` 使用成熟库，具体实现时再评估 `passlib` / `bcrypt` / `argon2`；
- session token 或 JWT 二选一，第一版优先简单、可审计、易撤销；
- token secret 只放 `.env` 或私有部署环境；
- `.env` 不提交公开仓库。

前端建议：

- 现有 mock login 逐步迁移到 auth API；
- 登录成功后保存最小必要登录态；
- 请求 context 从真实登录态和当前项目状态生成；
- 登录失败给出产品化错误提示，不暴露技术细节。

依赖原则：

- 不在设计阶段引入依赖；
- 密码哈希库和 token 库应在代码落地步骤中单独评估、单独测试；
- 不散装依赖；
- 不提交真实 token、secret、员工账号或密码。

## 6. 与 ContextOptions 的关系

登录成功后，后端应返回或生成：

- `user_id`
- `workspace_id`
- `default_project_id` 可选；
- `session_id` 或 session token；
- `role`
- `status`

前端不再硬编码 `internal_user_mock_001`。

后续 `context_options` 应由真实登录态和当前项目状态生成：

- `user_id` 来自当前登录用户；
- `workspace_id` 来自当前用户所属工作区；
- `project_id` 来自当前剧本项目；
- `session_id` 来自当前创作 / 编辑会话；
- `request_id` 每次请求生成；
- `source_stage` 按生成、导入、导出、质量评审等阶段设置；
- `context_policy` 默认 `current_project_only`。

所有生成、导入、导出、质量评审和 Usage Ledger 都应绑定 user / workspace / project / session。底层 LLM API Key 不是上下文边界，只是 provider 认证和计费凭证。

## 7. 与 Usage Ledger 的关系

`UsageLedgerEntry` 必须记录：

- `user_id`
- `workspace_id`
- `project_id`
- `session_id`
- `operation`
- `provider`
- `model`
- `purpose`
- `status`
- `request_id`
- `estimated_cost_cny`

第一版可以继续非持久化或使用 SQLite。进入内部长期使用和服务器部署前，至少需要明确持久化策略。

Usage Ledger 不应记录：

- 完整剧本文本；
- 完整上传文件内容；
- 完整 provider 原始响应；
- API Key；
- 密码；
- token；
- 本机绝对路径。

## 8. 安全边界

必须遵守：

- 不提交真实员工账号；
- 不提交密码；
- 不提交来自真实密码的 `password_hash` 样例；
- 不提交 JWT secret 或 session secret；
- 不提交 `.env`；
- 不在错误日志中记录密码；
- 不在错误日志中记录 token；
- 登录失败提示不泄露具体账号是否存在；
- 生产环境必须使用 HTTPS；
- 管理员重置密码流程后续单独设计；
- 公开仓库只保留 schema、service、测试和安全虚构样例。

密码与登录错误提示建议：

- 不提示“账号不存在”或“密码错误”中的具体哪一个；
- 使用统一提示，例如“账号或密码不正确”；
- 后续可增加失败次数限制和管理员解锁。

## 9. 分阶段落地路线

建议路线：

- 第 319 步：内部账号与权限落地文档；
- 第 320 步：Auth schema；
- 第 321 步：password policy helper + tests；
- 第 322 步：mock / in-memory auth service；
- 第 323 步：auth endpoints；
- 第 324 步：frontend login 从 mock 状态迁移到 auth API；
- 第 325 步：`context_options` 从真实登录态生成；
- 第 326 步：Usage Ledger 绑定真实 `user_id`；
- 第 327 步：部署前 auth security checklist。

每一步都应保持小闭环：

- 后端 pytest；
- 前端 build；
- e2e；
- 不提交真实账号；
- 不提交 secret；
- 不改变三入口剧本生成主流程。

## 10. 验收标准

本文档合格标准：

- 明确当前 mock auth 不等于正式权限；
- 明确内部 5～10 人使用范围；
- 明确 `username` 支持中文和英文；
- 明确密码规则；
- 明确 role / status；
- 明确和 `ContextOptions` / Usage Ledger 的关系；
- 明确安全边界；
- 不包含真实账号；
- 不包含真实密码；
- 不包含 API Key；
- 不包含 `.env`；
- 不包含真实员工、客户、剧本或上传文件内容。
