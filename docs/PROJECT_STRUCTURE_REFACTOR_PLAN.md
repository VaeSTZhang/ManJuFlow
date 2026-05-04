# Project Structure Refactor Plan｜项目结构梳理与渐进式重构计划

> 当前状态：老板已取消当前版本的右侧 AI 聊天界面、AI Assistant、`/api/assistant/chat` 和 `suggested_actions`。本文中关于 assistant 目录、AssistantPanel、assistant router / service 的内容仅作为历史结构方案归档，不纳入当前实施路线。当前结构治理应优先服务三入口剧本生成与改编、在线编辑、导入导出、用量记录、质量评审和后续分镜 / Prompt 工作流。

## 1. 设计目标

本计划用于在不破坏当前稳定功能的前提下，逐步整理 ManJuFlow 的代码与文档结构，避免随着 Phase 5 的上传、Auth、Assistant、UsageLedger、Workspace 增加而失控。

原则：

- 不做一次性大搬迁；
- 不为了“看起来整洁”破坏当前稳定链路；
- 以小闭环、可测试、可回滚为原则；
- 新增模块按清晰边界落位；
- 旧代码等功能稳定后逐步拆分。

当前项目已经具备 Phase 1～4 的稳定主链路，Phase 5 也已开始加入 Script Segmentation、上传文档、内部账户、Workspace Context Isolation 等设计。因此现在适合规划结构边界，但不适合马上做大规模重构。

## 2. 当前根目录判断

当前根目录结构总体合理：

- `apps`：前后端应用；
- `docs`：项目文档；
- `examples`：示例输入输出；
- `scripts`：本地开发脚本；
- `tests`：测试；
- `README.md`：项目主页；
- `.env.example`：配置模板；
- `.gitignore`：忽略规则。

本地存在 `.venv` 和 `.env` 是正常的，但必须确保不进入 Git。

建议后续检查 `.gitignore` 至少包含：

- `.venv/`
- `.env`
- `storage/`
- `node_modules/`
- `dist/`
- `*.tsbuildinfo`
- `__pycache__/`
- `*.pyc`

如果缺失，应单独开小步骤补充，不在本计划文档步骤中直接修改。

## 3. 后端结构建议

当前后端继续保持：

```text
apps/api/app/
├── schemas/
├── services/
├── routers/
├── prompts/
├── config.py
└── main.py
```

短期不改成复杂 DDD 或微服务。当前 Schema / Service / Router / Prompt 分层已经足够支撑 MVP 和公开仓库评审。

新增模块建议：

### Upload

```text
apps/api/app/schemas/upload.py
apps/api/app/services/upload_service.py
apps/api/app/routers/uploads.py
```

### Auth

```text
apps/api/app/schemas/auth.py
apps/api/app/services/auth_service.py
apps/api/app/routers/auth.py
```

### Assistant

```text
apps/api/app/schemas/assistant.py
apps/api/app/services/assistant_service.py
apps/api/app/routers/assistant.py
```

### UsageLedger

```text
apps/api/app/schemas/usage_ledger.py
apps/api/app/services/usage_ledger_service.py
```

规则：

- 不把上传逻辑塞进 `scripts.py`；
- 不把 auth 逻辑塞进 `main.py`；
- 不把 usage ledger 写散在各个 service；
- 不把真实 API Key 写进代码；
- Prompt 继续放 `apps/api/app/prompts/`；
- 真实 provider、真实账号、真实 storage 路径只进入私有部署环境。

## 4. 前端结构建议

当前 `App.tsx` 已经承载较多 workspace 逻辑，后续需要渐进拆分。

建议新增：

```text
apps/web/src/components/workspaces/
├── ScriptSegmentationWorkspace.tsx
├── IdeaToScriptWorkspace.tsx
├── StoryboardWorkspace.tsx
├── ImagePromptWorkspace.tsx
├── ImageGenerationWorkspace.tsx
└── ImageGenerationBundleWorkspace.tsx
```

```text
apps/web/src/components/assistant/
├── AssistantPanel.tsx
├── AssistantMessageList.tsx
├── AssistantComposer.tsx
└── AssistantSuggestedActions.tsx
```

```text
apps/web/src/components/auth/
├── LoginGate.tsx
├── MockLoginCard.tsx
└── CurrentUserBadge.tsx
```

```text
apps/web/src/components/uploads/
├── ScriptUploadPanel.tsx
└── UploadSourceCard.tsx
```

规则：

- 优先拆新增 workspace；
- 不一次性重构全部 `App.tsx`；
- 每次拆一个组件就运行 `npm run build`；
- 拆分后保持浏览器主链路验收；
- 不引入复杂状态管理，除非当前 React state 明显失控；
- 先保持 AppShell + Sidebar + Toast 的现有工作台结构。

## 5. docs 结构建议

`docs` 当前文件较多，但暂不立即搬迁。

未来建议整理为：

```text
docs/
├── phases/
├── design/
├── runbooks/
├── reference/
└── legal/
```

建议映射：

### phases

- `PHASE_1_SUMMARY.md`
- `PHASE_2_SUMMARY.md`
- `PHASE_3_SUMMARY.md`
- `PHASE_4_SUMMARY.md`
- `PHASE_5_*.md`

### design

- `WORKFLOW_REGISTRY_DESIGN.md`
- `FRONTEND_INFORMATION_ARCHITECTURE_PLAN.md`
- `COMFYUI_PROVIDER_TECHNICAL_DESIGN.md`
- `PROJECT_STRUCTURE_REFACTOR_PLAN.md`

### runbooks

- `LOCAL_DEV.md`
- `MODEL_COMPARISON_RUNBOOK.md`
- `COMFYUI_PRIVATE_DEPLOYMENT_RUNBOOK_DRAFT.md`

### reference

- `API_CONTRACT.md`
- `LLM_SETUP.md`
- `MVP_ROADMAP.md`

### legal

- `COOPERATION_TECH_ASSET_BOUNDARY_DRAFT.md`

说明：

- README 升级前可以先做 docs index 或文档导航；
- 不急着移动文件；
- 如果未来移动 docs，需要同步更新 README、文档链接和引用路径；
- 文档迁移应单独做小闭环。

## 6. storage 与上传文件边界

未来会新增 `storage/` 作为本地 runtime 文件目录：

```text
storage/
├── user_uploads/
├── assistant_conversations/
└── generated_exports/
```

要求：

- `storage/` 不进入 Git；
- 真实上传文件不进入公开仓库；
- 前端不读取本地路径；
- 后端通过 `source_id` 暴露 `extracted_text` 和 metadata；
- 生产部署时 storage 可迁移到对象存储或私有文件服务。

公开仓库可以保留 storage 设计说明和 mock 样例，但不能提交真实文件本体。

## 7. 渐进式重构顺序

建议顺序：

1. 新增 `PROJECT_STRUCTURE_REFACTOR_PLAN.md`；
2. 继续 Upload Source Schema；
3. 新增 upload service / endpoint；
4. 前端上传 UI；
5. 拆 `ScriptSegmentationWorkspace`；
6. 新增 Mock Internal Auth；
7. 拆 Auth 组件；
8. 新增 Assistant Panel；
9. README 中英双语升级；
10. 需要时再整理 docs 目录。

每一步都应有明确输入、输出、测试或构建验证。不要把结构整理和新功能开发混成一个大步骤。

## 8. 不做事项

当前暂不做：

- 不一次性移动所有 docs；
- 不一次性拆完 `App.tsx`；
- 不改成微服务；
- 不引入复杂 monorepo 工具；
- 不上 Redis / Celery / MinIO；
- 不接真实公司账号；
- 不提交 `storage/`；
- 不提交 `.env`；
- 不提交真实上传文件。

## 9. 验收标准

第 148.1 步验收标准：

- `docs/PROJECT_STRUCTURE_REFACTOR_PLAN.md` 已新增；
- 文档明确当前根目录总体合理；
- 文档明确后端新增 upload / auth / assistant / usage_ledger 的落位；
- 文档明确前端 workspaces / assistant / auth / uploads 组件拆分方向；
- 文档明确 docs 未来整理方向；
- 文档明确 `storage/` 不进入 Git；
- 文档明确渐进式重构，不做一次性大搬迁；
- 不修改代码；
- 不移动文件；
- 不引入敏感信息。
