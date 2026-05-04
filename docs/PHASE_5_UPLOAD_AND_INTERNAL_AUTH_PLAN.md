# Phase 5 Upload and Internal Auth Plan｜剧本文档上传与内部账户门禁方案

> 当前状态：老板已取消当前版本的右侧 AI 聊天界面、AI Assistant、`/api/assistant/chat` 和 `suggested_actions`。本文中关于 Assistant 的内容仅作为历史方案归档，不纳入当前实施路线。上传与内部账户方案当前应优先服务三入口剧本生成 / 改编、在线编辑、导入导出、用量记录、质量评审和后续分镜 / Prompt 工作流。

## 1. 设计目标

本方案用于明确：

- 已有剧本输入支持粘贴文本和上传 Word 文档两种方式；
- 上传文件保存、提取文本、进入 Script Segmentation 的流程；
- 所有 AI 功能在生产环境必须登录内部账户后才能使用；
- 登录用户、AI 功能账户、项目、workspace、用量审计之间的关系；
- 第五阶段按小闭环逐步落地，不一次性做复杂企业权限系统。

本步只写方案文档，不新增代码、不新增依赖、不接真实 DeepSeek、不写真实账号、不写真实员工信息、不写真实客户剧本。

## 2. 已有剧本输入的两种方式

### 方式 A：粘贴文本

流程：

```text
用户粘贴剧本文本
  -> 前端 Existing Script 输入框
  -> POST /api/scripts/segment
  -> ScriptSegmentationOutput
  -> Storyboard / ImagePrompt
```

说明：

- 这是第五阶段已完成的早期 mock 闭环；
- 适合快速验证 Script Segmentation 数据协议；
- 不涉及文件保存和文件解析；
- 前端直接把 `script_text` 发给后端。

### 方式 B：上传 Word 文档

流程：

```text
用户上传 .docx
  -> POST /api/uploads/script
  -> 后端保存文件到 storage/user_uploads/
  -> 后端提取 extracted_text
  -> 返回 source_id + extracted_text + metadata
  -> 前端填入 Script Segmentation Workspace
  -> 用户确认后 POST /api/scripts/segment
```

说明：

- 第一版优先支持 `.docx`；
- 暂不优先支持 `.doc`；
- `.doc` 可提示用户另存为 `.docx`；
- 后续如必须支持 `.doc`，再单独设计转换服务；
- 前端不读取后端本地路径，只读取 API 返回的 `source_id` / `extracted_text` / metadata。

## 3. 上传文件保存策略

本地开发阶段建议目录：

```text
storage/user_uploads/<workspace_id>/<source_id>/
```

建议文件：

- `original.docx`
- `extracted_text.txt`
- `metadata.json`

metadata 建议字段：

- `source_id`
- `project_id`
- `workspace_id`
- `user_id`
- `ai_account_id`
- `original_filename`
- `content_type`
- `file_size`
- `sha256`
- `created_at`
- `extraction_status`
- `extracted_text_length`

要求：

- `storage/` 必须在 `.gitignore`；
- 真实上传文件不进入公开仓库；
- 真实客户剧本不进入公开仓库；
- 公开仓库只使用 mock 样例；
- 前端和下游服务只依赖 `source_id`、`extracted_text` 和 metadata，不依赖后端本地路径。

## 4. Word 文档解析策略

解析策略：

- 第一版支持 `.docx`；
- 后端后续可以使用 `python-docx` 提取段落文本；
- 新增依赖必须单独小闭环引入并测试；
- 不在本方案步骤中直接新增依赖；
- `.doc` 暂不处理或提示转换；
- 解析失败要返回清晰错误；
- 提取文本后进入 Script Segmentation，而不是直接让前端读取文件路径。

后续解析时应注意：

- 保留段落顺序；
- 尽量保留基础换行；
- 对空段落做轻量清理；
- 不在日志中输出完整剧本文本；
- 不把原始文件或提取文本提交 Git。

## 5. 内部账户登录门禁原则

真正生产环境中，所有 AI 功能必须登录后使用。

受保护能力包括：

- 灵感生成剧本；
- 已有剧本切分；
- 分镜生成；
- 绘图 Prompt 生成；
- 图片生成 mock / bundle；
- AI Assistant Chat；
- 文件上传；
- 导出生产资产；
- 查看历史记录和用量。

未登录时：

- 前端显示登录入口；
- 不允许调用生产接口；
- 不展示 workspace 主功能；
- 可展示 README / demo 说明，但不可执行生成。

登录不是只为了挡住入口，也是为了让每次 AI 调用具备用户归属、项目归属、成本归属和审计记录。

## 6. MVP 内部账户实现策略

不要一开始做复杂企业权限系统，建议分阶段推进。

### 阶段 A：Mock Internal Auth

- 前端提供 mock 登录卡片；
- 输入 mock 员工名或选择 mock user；
- 生成 mock user session；
- AppShell 只有登录后显示；
- 所有请求附带 mock `user_id` / `ai_account_id` / `workspace_id`；
- 用于验证 UI、上下文归属、用量记录字段。

### 阶段 B：Backend Session Mock

- 后端新增 auth schema / mock service；
- `POST /api/auth/login`；
- `GET /api/auth/me`；
- `POST /api/auth/logout`；
- 前端从后端读取当前用户；
- 暂不接真实公司账号。

### 阶段 C：SQLite Local Auth

- users / ai_accounts / sessions 入库；
- 支持 session 过期；
- 支持基础角色；
- 不进入公开仓库真实数据；
- 本地数据库文件不提交 Git。

### 阶段 D：Company Private Auth

- 接入公司真实账号体系；
- 权限、部门、角色、用量统计；
- 管理员管理 provider credentials；
- 真实员工信息、真实权限策略和真实 provider key 只进入私有部署环境。

## 7. Auth 与 UsageLedger 的关系

每次 AI 调用都应该能关联：

- `user_id`
- `ai_account_id`
- `project_id`
- `workspace_id`
- `feature_name`
- `operation_type`
- `provider`
- `model`
- token usage
- `estimated_cost_cny`

登录不是只为了权限，也是为了审计和成本归属。

示例：

```text
currentUser
  -> AIWorkspaceAccount
  -> Script Segmentation / Assistant / ImagePrompt request
  -> UsageLedger
  -> cost and audit report
```

## 8. Auth 与 Workspace Context Isolation 的关系

登录后仍然不能跨项目乱读。

每次请求必须明确：

- `activeProject`
- `activeWorkspace`
- `currentUser`
- `aiAccount`
- `contextRefs`

Assistant 和内容生产链路默认只能读取当前 project / workspace 的上下文。

规则：

- 用户身份解决“谁在操作”；
- project / workspace 解决“操作哪个项目”；
- context refs 解决“本次 AI 可以读取哪些内容”；
- UsageLedger 解决“这次操作消耗了多少、归属到哪里”。

## 9. 建议后续步骤调整

建议路线：

- 第 148 步：Upload and Internal Auth Plan 文档；
- 第 149 步：Upload Source Schema；
- 第 150 步：Upload mock service；
- 第 151 步：`POST /api/uploads/script` mock endpoint；
- 第 152 步：前端上传 Word 文档 mock UI；
- 第 153 步：Mock Internal Auth 前端门禁；
- 第 154 步：Auth Schema / mock service / endpoint；
- 第 155 步：登录态接入 workspace 请求；
- 第 156 步：Script Segmentation 结果带入 Storyboard；
- 第 157 步：README 中英双语专业升级。

说明：

- 上传和 auth 都应按小闭环推进；
- 不要一次性实现完整企业权限系统；
- 不要在公开仓库接真实公司账号；
- 不要把真实上传文件或真实员工信息放进测试样例。

## 10. 公开仓库安全边界

公开仓库可以包含：

- upload schema；
- upload mock service；
- mock auth；
- mock users；
- mock ai accounts；
- 文档；
- 虚构测试样例；
- `.env.example` 占位变量。

公开仓库不能包含：

- 真实上传剧本；
- 真实员工账号；
- 真实聊天记录；
- 真实客户资料；
- 真实 API Key；
- 真实账单；
- 生产数据库；
- `storage/` 文件本体；
- 公司内部身份系统配置。

公开仓库仍然只承载可评审架构、本地 mock demo、数据协议和安全集成边界。

## 11. 验收标准

第 148 步验收标准：

- `docs/PHASE_5_UPLOAD_AND_INTERNAL_AUTH_PLAN.md` 已新增；
- 文档明确粘贴文本和上传 `.docx` 两种输入方式；
- 文档明确 `.doc` 暂不优先支持；
- 文档明确上传文件保存到 `storage/user_uploads/`；
- 文档明确 `extracted_text` 通过 API 返回给前端；
- 文档明确生产环境所有 AI 功能必须登录；
- 文档明确 mock auth -> backend session -> SQLite -> company auth 的分阶段路线；
- 文档明确 Auth 与 UsageLedger / Workspace Context Isolation 的关系；
- 文档明确公开仓库安全边界；
- 不修改代码；
- 不新增依赖；
- 不引入真实敏感信息。
