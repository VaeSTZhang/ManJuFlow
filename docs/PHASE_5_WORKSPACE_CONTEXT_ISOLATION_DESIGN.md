# Phase 5 Workspace Context Isolation Design｜项目工作区上下文隔离设计

## 1. 设计目标

本设计用于解决未来公司多员工、多项目组、多工作区并行使用时，AI 不应串项目、不应读取错误上下文、不应把一个项目的角色、剧情、Prompt 回复到另一个项目中。

目标是保证：

- 每次 AI 请求都有明确 `project_id` / `workspace_id` / `user_id`；
- Assistant Conversation 归属于具体项目和工作区；
- 上传文件、剧本切分、分镜、Prompt、图片任务都归属于具体项目；
- AI 默认只能读取当前项目允许的上下文；
- 跨项目引用必须显式授权；
- `UsageLedger` 也能按项目和工作区统计。

本步只写设计文档，不新增 Schema、不新增 service、不新增数据库代码，也不引入真实员工、真实客户、真实项目资料或真实 key。

## 2. 为什么仅有员工账号不够

每个员工有 `AIWorkspaceAccount` 只能解决“谁在使用”，但不能解决“他正在使用哪个项目”。

典型风险：

- 同一个员工同时参与多个短剧项目；
- 同一个 Assistant 聊天窗口误读取另一个项目的剧本；
- 美术在 A 项目生成 Prompt，却引用了 B 项目角色；
- 编剧要求修改第 3 集，AI 不知道是哪一个项目的第 3 集；
- `UsageLedger` 只记录 `user_id`，不记录 `project_id`，会导致项目成本统计错误；
- 项目交接时无法判断某条生成结果属于哪个项目和工作区。

结论：必须同时设计 `user_id`、`ai_account_id`、`project_id`、`workspace_id`、`conversation_id`。

## 3. 核心实体建议

建议核心实体包括 `Project`、`Workspace`、`WorkspaceContext` 和 `ConversationScope`。

### Project

表示一个内容生产项目。

建议字段：

- `project_id`
- `project_title`
- `project_type`
- `status`
- `owner_user_id`
- `created_at`
- `updated_at`
- `metadata`

### Workspace

表示项目内的功能工作区。

建议字段：

- `workspace_id`
- `project_id`
- `workspace_type`
- `title`
- `status`
- `created_at`
- `updated_at`
- `metadata`

`workspace_type` 建议：

- `idea`
- `script`
- `script_segmentation`
- `storyboard`
- `image_prompt`
- `image_generation`
- `assistant`
- `asset_manager`

### WorkspaceContext

表示当前 workspace 可供 AI 使用的上下文。

建议字段：

- `context_id`
- `project_id`
- `workspace_id`
- `context_type`
- `ref_id`
- `ref_type`
- `summary`
- `created_at`
- `metadata`

`ref_type` 建议：

- `upload_source`
- `script_output`
- `script_segment`
- `storyboard_output`
- `image_prompt_output`
- `image_generation_bundle`
- `assistant_message`

### ConversationScope

表示一次 Assistant 会话的上下文边界。

建议字段：

- `conversation_id`
- `project_id`
- `workspace_id`
- `user_id`
- `ai_account_id`
- `allowed_context_refs`
- `denied_context_refs`
- `allow_cross_project_context`
- `created_at`
- `metadata`

默认：

```text
allow_cross_project_context = false
```

## 4. AI 请求上下文边界

每次 AI 请求都应该显式携带：

- `user_id`
- `ai_account_id`
- `project_id`
- `workspace_id`
- `conversation_id`
- `current_workspace`
- `selected_text`
- `context_refs`
- `allowed_context_types`
- `denied_context_types`

默认规则：

- 只读取当前 `project_id`；
- 只读取当前 `workspace_id` 或明确传入的 `context_refs`；
- 不读取其他项目；
- 不读取未授权上传文件；
- 不读取其他员工私有会话；
- 不把历史所有聊天无脑塞进上下文；
- 只传必要摘要和当前任务相关内容。

上下文构造应是显式、可审计、可复现的，而不是“把系统里能拿到的内容全部拼进 prompt”。

## 5. Assistant Chat 隔离规则

Assistant Chat 必须遵守：

- 一个 `conversation_id` 绑定一个 `project_id`；
- 一个 `conversation_id` 默认绑定一个 `workspace_id`；
- 如果用户切换项目，必须开启新的 conversation 或显式切换 scope；
- Assistant 回复时必须知道当前 `project_title`；
- Assistant suggested_actions 必须带 `target_project_id` / `target_workspace_id`；
- 应用 suggested action 前必须校验 `project_id` 是否一致；
- 不允许 Assistant 自动修改其他项目数据；
- 跨项目参考必须显式确认。

Assistant 可以帮助用户导航和建议操作，但不应绕过项目边界和确认机制。

## 6. Script Segmentation 隔离规则

`ExistingScriptInput` / `ScriptSegmentationOutput` 应预留或使用：

- `project_id`
- `workspace_id`
- `source_id`
- `user_id`
- `ai_account_id`
- `metadata`

规则：

- `source_id` 必须属于当前 `project_id` 或 `workspace_id`；
- 切分结果写回当前 project；
- 切分结果进入 Storyboard 时必须携带 `project_id` / `workspace_id`；
- 不允许拿 A 项目的 uploaded source 生成 B 项目的 script segments；
- 如果早期 Schema 暂未正式字段化 `project_id`，应在 `metadata` 中预留并在后续步骤补齐。

## 7. Storyboard / ImagePrompt / ImageGeneration 链路隔离规则

以下对象都应最终带上 project / workspace 元信息：

- `StoryboardOutput`
- `ImagePromptOutput`
- `ImageGenerationBundleOutput`
- `AssetItem`
- `RenderTaskItem`

早期可以通过 `metadata` 预留，后续再逐步正式字段化。

规则：

- Storyboard 来源必须可追溯到 script 或 script_segment；
- ImagePrompt 来源必须可追溯到 storyboard；
- ImageGeneration 来源必须可追溯到 image_prompt；
- Asset 必须可追溯到 `project_id` / `prompt_id` / `shot_id`；
- RenderTask 必须可追溯到 `project_id` / `provider` / `workflow_name`。

这能避免内容生成链路在多项目并发时串角色、串剧情、串 Prompt 或串资产。

## 8. UsageLedger 与项目成本归属

`UsageLedger` 必须预留：

- `project_id`
- `workspace_id`
- `conversation_id`
- `feature_name`
- `operation_type`
- `provider`
- `model`
- token usage
- `estimated_cost_cny`

这样可以统计：

- 某个项目总共花了多少；
- 某个员工在某项目花了多少；
- Assistant Chat 和内容生产分别花了多少；
- 哪个 workspace 消耗最多；
- 哪些失败请求造成浪费。

如果只按 `user_id` 统计，会丢失项目成本归属；如果只按 `project_id` 统计，会丢失人员责任链。两者都必须保留。

## 9. 前端工作台隔离设计

前端 AppShell / Sidebar 后续应明确：

- 当前 `activeProject`；
- 当前 `activeWorkspace`；
- AssistantPanel 读取 `activeProject` / `activeWorkspace`；
- 切换项目时清空或切换 Assistant conversation；
- 每个 workspace 的结果只属于当前 project；
- 用户上传文件后，`source_id` 绑定当前 project；
- suggested action 按 `target_workspace` 进入对应工作区；
- 不在前端全局混放多个项目的数据。

第五阶段早期可以先不做完整多项目 UI，但类型和上下文设计要预留。当前 Sidebar 管理的是 workspace，未来应增加 project selector 或 project context provider。

## 10. 安全与误操作防护

建议规则：

- 所有跨项目动作都 `requires_confirmation=true`；
- Assistant suggested action 默认只作用当前 project；
- 删除、覆盖、应用改写等动作要有确认；
- 上传文件不能被其他项目默认读取；
- conversation scope 不应自动扩大；
- 日志中不输出完整敏感剧本；
- 公开仓库只使用虚构 `project_id` / `workspace_id`。

任何可能改变数据、读取跨项目上下文或导出敏感内容的动作，都应先进行显式确认和 scope 校验。

## 11. 第五阶段落地策略

不要一次性实现完整权限系统。建议分阶段落地。

### 阶段 A：Schema metadata 预留

- 在 Script Segmentation Schema 中保留 `workspace_id` / `user_id` / `ai_account_id`；
- 后续逐步加入 `project_id`；
- `metadata` 中可暂存 context 信息。

### 阶段 B：Assistant mock scope

- Assistant mock 输入输出带 `project_id` / `workspace_id`；
- suggested action 带 `target_workspace`；
- 默认不允许跨项目。

### 阶段 C：前端 active workspace

- Sidebar 管理 `activeWorkspace`；
- AssistantPanel 读取当前 workspace；
- 后续增加 `activeProject`。

### 阶段 D：SQLite / 私有部署

- Project / Workspace / Conversation / UsageLedger 入库；
- 做权限和审计；
- 私有环境中接入真实公司账号体系。

## 12. 对后续步骤的影响

第 142 步 script segmentation mock service 应使用并保留 `workspace_id` / `user_id` / `ai_account_id` / `metadata`。

后续如果需要，可在 `ExistingScriptInput` 中增加 `project_id`。

Assistant Schema 设计时必须包含：

- `project_id`
- `workspace_id`
- `conversation_id`

`UsageLedger` 设计必须包含：

- `project_id`
- `workspace_id`

建议路线：

- 第 141.1 步：Workspace Context Isolation 文档；
- 第 142 步：script segmentation mock service；
- 第 143 步：`POST /api/scripts/segment`；
- 第 144 步：Script Segmentation service / endpoint tests；
- 第 145 步：前端 ScriptSegmentation 类型和 API；
- 第 146 步：Sidebar 新增“已有剧本切分” workspace；
- 第 147 步：切分结果带入 Storyboard / ImagePrompt；
- 第 148 步：AI Assistant Panel 设计文档；
- 第 149 步：Assistant Chat Schema / mock service / endpoint，必须包含 `project_id` / `workspace_id` / `conversation_id`；
- 第 150 步：前端 AssistantPanel mock UI。

## 13. 验收标准

第 141.1 步验收标准：

- `docs/PHASE_5_WORKSPACE_CONTEXT_ISOLATION_DESIGN.md` 已新增；
- 文档明确为什么员工账号不等于项目上下文隔离；
- 文档包含 Project / Workspace / WorkspaceContext / ConversationScope 草案；
- 文档明确 AI 请求必须带 `project_id` / `workspace_id` / `user_id`；
- 文档明确 Assistant Chat 不应跨项目读取；
- 文档明确 Script Segmentation `source_id` 不能跨项目误用；
- 文档明确 `UsageLedger` 应带 `project_id` / `workspace_id`；
- 文档明确前端 `activeProject` / `activeWorkspace` 设计方向；
- 不修改代码；
- 不引入真实员工、真实客户、真实项目资料或真实 key。
