# Phase 5 Data Persistence and Assistant Context Design｜上传文件、聊天记录与上下文持久化设计

> 当前状态：老板已取消当前版本的右侧 AI 聊天界面、AI Assistant、`/api/assistant/chat` 和 `suggested_actions`。本文仅作为历史方案归档，用于保留早期对上传文件、聊天记录和上下文隔离的思考，不纳入 Dramora 当前实施路线。当前版本聚焦三入口短剧剧本生成 / 改编、在线编辑、Word / TXT / JSON 导入导出、创作模型选择、用量记录、质量评审，以及后续“短剧剧本 → 分镜 → Prompt”工作流。

## 1. 设计目标

本设计用于第五阶段正式写代码前明确：

- 用户上传文件保存策略；
- 前端读取上传内容的 API 边界；
- 已有剧本上传 / 粘贴后如何进入 Script Segmentation；
- Assistant Chat 如何与创作链路 LLM 隔离；
- Assistant 聊天记录如何保存、回溯、审计；
- 本地开发与未来私有部署的迁移边界。

本步仍然是设计文档，不直接写代码，不新增 Schema，不新增 service，不新增 router，不新增数据库实现，也不修改 `.env.example`。

## 2. 为什么必须提前设计持久化

第五阶段会引入“已有剧本输入”和“AI Assistant 聊天协作”。如果不提前设计持久化边界，后续容易出现以下问题：

- 上传文件散落在项目目录；
- 真实剧本误提交公开仓库；
- 前端依赖本地路径，后续部署无法迁移；
- 聊天记录无法回溯；
- Assistant 上下文和创作链路混用；
- 同一家 LLM provider 被不同业务链路混乱调用；
- 后期难以做项目级历史记录和资产管理；
- 难以区分临时草稿、正式资产、上下文快照和审计记录。

因此，Script Segmentation 和 Assistant 开发前，需要先明确文件、文本、上下文、聊天记录和 LLM 调用的边界。

## 3. 用户上传文件保存策略

本地开发阶段建议：

- 文件本体保存到 runtime storage；
- 建议目录：`storage/user_uploads/`；
- `storage/` 必须进入 `.gitignore`；
- 不提交任何真实上传文件；
- 每次上传生成 `source_id`；
- 保存 original file、`extracted_text`、metadata；
- 前端不直接读取本地文件路径。

建议目录结构：

```text
storage/
  user_uploads/
    <workspace_id>/
      <source_id>/
        original.<ext>
        extracted_text.txt
        metadata.json
```

metadata 建议包含：

- `source_id`
- `workspace_id`
- `project_title`
- `original_filename`
- `content_type`
- `file_size`
- `sha256`
- `created_at`
- `source_type`
- `extraction_status`
- `extracted_text_length`

未来私有部署：

- 文件本体迁移到对象存储或私有文件服务；
- 元数据进入 SQLite / PostgreSQL；
- 公开仓库只保留接口、mock、文档和安全边界；
- 公开仓库不保存真实上传文件、真实客户剧本或真实生产素材。

## 4. 前端如何读取上传内容

前端不应该直接读取后端磁盘路径。

正确链路：

```text
用户上传文件
  -> POST /api/uploads/script
  -> 后端保存文件并提取文本
  -> 返回 source_id + extracted_text + metadata
  -> 前端将 extracted_text 填入 Script Segmentation Workspace
  -> 用户确认后调用 POST /api/scripts/segment
```

建议未来 endpoint：

- `POST /api/uploads/script`
- `GET /api/uploads/{source_id}`
- `DELETE /api/uploads/{source_id}` 或 archive
- `POST /api/scripts/segment`

说明：

- 第五阶段早期可以先支持粘贴文本；
- 文件上传可以稍后独立小闭环；
- 但数据结构和保存边界必须提前设计；
- 前端展示的是 `extracted_text`、metadata 和 `source_id`；
- 前端不展示、不保存、不依赖后端本地文件路径。

## 5. Script Segmentation 与 Upload Source 的关系

`ExistingScriptInput` 未来可以支持两种输入方式。

方式 A：直接传 `script_text`

```text
用户粘贴剧本文本
  -> ExistingScriptInput.script_text
  -> POST /api/scripts/segment
```

方式 B：传 `source_id`

```text
用户上传文件
  -> 后端提取文本
  -> 返回 source_id
  -> ExistingScriptInput.source_id
  -> 后端读取 extracted_text
  -> POST /api/scripts/segment
```

建议 `ExistingScriptInput` 字段预留：

- `project_title`
- `script_text`
- `source_id`
- `source_type`
- `target_segment_level`
- `language`
- `extra_requirements`

规则：

- `script_text` 和 `source_id` 至少提供一种；
- 如果两者都提供，优先使用 `script_text`，或在 service 中明确另一套规则；
- `source_id` 只引用后端已保存的上传源；
- 不把本地路径返回给前端；
- 所有下游都使用文本内容和结构化结果，不依赖文件路径。

## 6. Assistant LLM 与创作 LLM 的隔离策略

AI Assistant 后续肯定会接入大模型，但必须与已有 AI 改编、原创、扩写、分镜、Prompt 生成功能隔离。

推荐策略：

- Assistant 使用独立配置命名空间；
- 可以同样使用 DeepSeek，但建议使用单独 API Key；
- 更高隔离可使用单独 DeepSeek 账号；
- 代码层使用独立 `assistant_service`；
- prompt 层使用独立 assistant prompt；
- endpoint 层使用 `POST /api/assistant/chat`；
- 日志和 metadata 标明 assistant provider / model；
- 不让 Assistant 直接复用 script / storyboard / image_prompt service 的业务 prompt。

建议环境变量命名：

```env
ASSISTANT_GENERATION_MODE=mock / llm
ASSISTANT_LLM_PROVIDER=deepseek
ASSISTANT_LLM_MODEL=...
ASSISTANT_DEEPSEEK_API_KEY=...
ASSISTANT_REQUEST_TIMEOUT_SECONDS=...
```

说明：

- 底层可以复用通用 `LLMClient` 的 HTTP 能力；
- 业务配置、prompt、上下文、返回结构必须隔离；
- Assistant 的对话上下文不应污染创作链路生成 prompt；
- 创作链路的 Script / Storyboard / ImagePrompt service 不应隐式读取 Assistant 对话。

## 7. Assistant 聊天记录保存策略

聊天记录应该保存，原因包括：

- 回溯创作过程；
- 追踪谁提出了什么修改建议；
- 恢复上下文；
- 分析 suggested actions；
- 后续做项目历史记录；
- 方便合作方评审工作流价值。

建议保存对象：

- `AssistantConversation`
- `AssistantMessage`
- `AssistantSuggestedActionRecord`
- `AssistantContextSnapshot`

### AssistantConversation

建议字段：

- `conversation_id`
- `workspace_id`
- `project_title`
- `title`
- `created_at`
- `updated_at`
- `status`
- `metadata`

### AssistantMessage

建议字段：

- `message_id`
- `conversation_id`
- `role`
- `content`
- `created_at`
- `provider`
- `model`
- `current_workspace`
- `token_usage`
- `metadata`

### AssistantSuggestedActionRecord

建议字段：

- `action_id`
- `conversation_id`
- `message_id`
- `action_type`
- `label`
- `target_workspace`
- `payload`
- `confidence`
- `requires_confirmation`
- `applied_at`
- `status`

### AssistantContextSnapshot

建议字段：

- `snapshot_id`
- `conversation_id`
- `message_id`
- `idea_ref`
- `script_ref`
- `script_segments_ref`
- `storyboard_ref`
- `image_prompt_ref`
- `upload_source_ref`
- `metadata`

## 8. 本地持久化建议

第五阶段早期可分层推进。

### 阶段 A：mock / memory

- Assistant 返回固定 reply + suggested_actions；
- 不长期保存；
- 仅验证 UI、Schema、service 和 suggested actions 链路。

### 阶段 B：本地文件 / JSONL

- 可保存简单 conversation jsonl；
- 适合早期调试；
- 不适合长期复杂查询；
- 仍需确保文件位于 `storage/`，不提交 Git。

### 阶段 C：SQLite

- 推荐作为第五阶段正式可用版本；
- 保存 uploads metadata、assistant conversations、messages、actions、context snapshots；
- 文件本体仍在 `storage/`；
- 便于后续迁移 PostgreSQL；
- 适合本地 MVP 和私有单机部署。

### 阶段 D：私有部署

- PostgreSQL / 对象存储 / 私有资产库；
- 支持权限、检索、审计和项目历史；
- 真实客户文件、真实聊天记录、真实账号信息只进入私有环境。

说明：

虽然不考虑成本，也要避免过早上复杂基础设施。质量优先不等于一开始引入所有重型组件。当前推荐先设计 SQLite-ready 数据模型，后续按小闭环落地。

## 9. 公开仓库安全边界

公开仓库可以包含：

- upload schema；
- upload mock service；
- assistant schema；
- assistant mock service；
- SQLite 表结构草案；
- `storage` 目录说明；
- `.gitignore` 规则；
- 虚构样例；
- 文档。

公开仓库不能包含：

- 真实用户上传剧本；
- 真实客户文件；
- 真实聊天记录；
- DeepSeek API Key；
- `.env`；
- 真实账号信息；
- 个人隐私；
- 合作方资料；
- 真实服务器地址；
- 生产数据库；
- 生产 storage 文件。

## 10. 建议后续步骤调整

原第 141 步之前插入本设计文档后，后续步骤建议调整为：

- 第 140 步：Phase 5 方案文档，已完成；
- 第 140.1 步：数据持久化与 Assistant 上下文设计文档；
- 第 141 步：新增已有剧本切分 Schema；
- 第 142 步：新增 script segmentation mock service；
- 第 143 步：新增 `POST /api/scripts/segment`；
- 第 144 步：新增 Script Segmentation 后端测试；
- 第 145 步：前端新增 ScriptSegmentation 类型和 API；
- 第 146 步：Sidebar 新增“已有剧本切分” workspace；
- 第 147 步：切分结果带入 Storyboard / ImagePrompt；
- 第 148 步：AI Assistant Panel 设计文档；
- 第 149 步：Assistant Chat Schema / mock service / endpoint；
- 第 150 步：前端右侧 AssistantPanel mock UI；
- 第 151 步：Assistant suggested actions；
- 第 152 步：上传文件 API 设计或实现；
- 第 153 步：聊天记录本地持久化设计或实现；
- 第 154 步：阶段性浏览器验收。

## 11. 验收标准

第 140.1 步验收标准：

- `docs/PHASE_5_DATA_PERSISTENCE_AND_ASSISTANT_CONTEXT_DESIGN.md` 已新增；
- 文档明确上传文件保存位置；
- 文档明确前端读取上传内容的 API 边界；
- 文档明确 `source_id` / `extracted_text` 进入 Script Segmentation 的路径；
- 文档明确 Assistant LLM 与创作 LLM 隔离；
- 文档建议 Assistant 使用独立 DeepSeek API Key 或独立账号；
- 文档明确聊天记录需要保存；
- 文档包含 Conversation / Message / SuggestedAction / ContextSnapshot 草案；
- 文档明确本地 `storage`、SQLite、未来私有部署迁移路径；
- 文档明确公开仓库安全边界；
- 不修改代码；
- 不引入敏感信息。
