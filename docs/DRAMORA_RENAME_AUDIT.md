# Dramora Rename Audit｜品牌重命名残留审计

## 1. 审计目标

本次审计用于保证 Dramora｜剧作工坊 对外品牌统一，同时避免盲目全局替换破坏历史文档、API、包名、模块名或运行脚本。

成熟项目改名通常不是追求立刻“零残留”，而是先统一用户可见层和当前开发入口，再分批处理内部兼容项。历史代号、旧阶段记录和稳定 API 需要按风险分类处理。

本次审计只记录 ManJuFlow / 漫剧流 / manjuflow 残留，不做大规模替换，不修改代码，不修改 package.json，不修改 API 路径，不修改历史文档内容。

## 2. 当前命名状态

- 对外品牌：Dramora｜剧作工坊
- GitHub 仓库：VaeSTZhang/Dramora
- 本地目录：/Users/zhangtritsen/Desktop/Code/Dramora
- 早期工程代号：ManJuFlow

当前 README 和本地开发入口已经说明 ManJuFlow 是早期工程代号，公开路径示例已改为 Dramora。

## 3. 成熟团队改名原则

- 用户可见层优先统一：浏览器标题、首页、README 默认页、演示材料、公开仓库展示应优先使用 Dramora｜剧作工坊。
- 当前开发入口优先统一：当前本地启动、测试、构建、配置说明应使用 Dramora 路径，避免技术组接手时误用旧目录。
- 历史记录可以保留旧代号：阶段总结、测试记录、旧方案文档中的 ManJuFlow 可以作为历史上下文保留。
- API / package / module 不能无计划大改：API 标题、包名、模块名、导出文件名前缀、package name 可能影响构建、依赖、测试或外部调用，应单独评估。
- 大规模重命名必须分批、可测试、可回滚：每批只处理一个层级，修改后运行对应测试和构建，再决定是否继续。

## 4. 残留分类

### A. 必须修改

必须修改的是当前用户或接手团队直接看到、且不属于历史记录的旧品牌残留。

本次 grep 发现的候选项：

- `apps/web/index.html`：浏览器标题仍为 `ManJuFlow｜漫剧流`，这是用户可见层，应改为 `Dramora｜剧作工坊`。
- `apps/api/app/main.py`：FastAPI 文档标题仍为 `ManJuFlow API`。如果 `/docs` 是当前演示或技术评审入口，应改为 `Dramora API`。
- `scripts/dev_api.sh`：脚本注释和启动输出仍显示 ManJuFlow。该脚本是当前开发入口，输出文案建议统一为 Dramora。
- `docs/BOSS_DEMO_SCRIPT.md`：老板演示脚本正文仍多处用 ManJuFlow 描述当前产品价值。作为演示材料，建议在下一步改为 Dramora，必要时保留一句“ManJuFlow 是早期工程代号”。
- `docs/MARKET_TRIAL_READINESS_PLAN.md`：市场试用说明中仍以 ManJuFlow 描述当前市场试用版。该文档仍作为入口规划时，应改为 Dramora。
- `docs/API_CONTRACT.md`：标题为 `ManJuFlow｜漫剧流 API Contract`。如果继续作为当前 API 入口文档，应改为 Dramora。

README 中仍出现 ManJuFlow，但目前是解释“早期工程代号”，不属于必须修改。

### B. 建议修改

建议修改的是不一定立即影响用户，但会影响可读性、交接体验或品牌一致性的残留。

本次 grep 发现的候选项：

- `apps/web/package.json`：`name` 仍为 `manjuflow-web`。建议后续单独评估是否改为 `dramora-web`。
- `apps/web/package-lock.json`：随 package name 派生，只有在修改 `apps/web/package.json` 后再同步更新。
- `apps/web/src/App.tsx`：导出文件名仍使用 `manjuflow-script-output.json`、`manjuflow-storyboard-output.json`。这是用户下载文件名，建议后续单独改为 dramora 前缀并做前端构建验证。
- `apps/api/app/config.py`：默认 `app_name` 仍为 `ManJuFlow`。如果该字段用于状态接口或展示文案，建议后续改为 Dramora，并运行后端测试。
- `apps/api/app/schemas/upload.py`、`apps/api/app/schemas/script_segmentation.py`：字段描述中仍写 `ManJuFlow 内部 AI 功能账户 ID`。如果这些 schema 会出现在 OpenAPI 文档，建议后续改为 Dramora。
- `docs/FRONTEND_LOCALIZATION_AND_PROMPT_LANGUAGE_GUIDE.md`、`docs/INPUT_LIMITS_AND_EDITOR_UX_PLAN.md`、`docs/PROJECT_STRUCTURE_REFACTOR_PLAN.md`、`docs/PROJECT_STRUCTURE_THREE_ENTRY_REFACTOR_PLAN.md`、`docs/PHASE_5A_PRODUCTIZATION_EXECUTION_PLAN.md`、`docs/PHASE_5_THREE_ENTRY_SCRIPT_WORKBENCH_REDESIGN.md`、`docs/PHASE_5_TEXT_TO_PROMPT_WORKBENCH_PLAN.md`、`docs/PHASE_5_USER_ACCOUNT_AND_USAGE_LEDGER_DESIGN.md`：这些偏产品或架构设计的文档如果仍作为当前规划入口，应逐步改为 Dramora。
- `docs/MIMO_INTEGRATION_PLAN.md`、`docs/LLM_TEST_LOG.md`、`docs/MODEL_COMPARISON_*`：模型接入与模型对比资料可在下一轮整理时统一改标题或增加 Dramora 注释，但不建议本步混入代码改动。

根目录 `package.json` 当前不存在；本次 grep 对 `package.json` 报 `No such file or directory`，不代表有根目录 package 残留。

### C. 可历史保留

可历史保留的是阶段总结、旧开发记录、早期方案和历史上下文中的旧代号。

本次 grep 发现的候选项：

- `docs/PHASE_1_SUMMARY.md`
- `docs/PHASE_2_PROGRESS.md`
- `docs/PHASE_2_SUMMARY.md`
- `docs/PHASE_3_PROGRESS.md`
- `docs/PHASE_3_SUMMARY.md`
- `docs/PHASE_4_IMAGE_GENERATION_PLAN.md`
- `docs/COMFYUI_PRIVATE_DEPLOYMENT_RUNBOOK_DRAFT.md`
- `docs/COMFYUI_PROVIDER_TECHNICAL_DESIGN.md`
- `docs/DEMO_SCRIPT.md`
- `docs/README_BILINGUAL_UPGRADE_PLAN.md`
- `docs/COOPERATION_TECH_ASSET_BOUNDARY_DRAFT.md`
- `docs/DOCUMENT_ROUND_TRIP_PLAN.md`

这些文档记录的是 ManJuFlow 阶段的历史、方案或早期边界，不需要为了品牌统一而破坏原始记录。后续如果需要对外展示，应另建当前版文档，而不是改写历史。

### D. 暂不修改

暂不修改的是可能影响构建、兼容性、测试或外部调用的内部标识。

本次 grep 发现的候选项：

- `apps/web/package.json` 中的 `manjuflow-web`：涉及 package lock 和前端构建，建议单独修改并验证。
- `apps/web/package-lock.json` 中的 `manjuflow-web`：应随 package name 修改自动同步，不手动孤立修改。
- `apps/api/app/main.py` 中的 FastAPI title：虽然用户可见，但属于后端代码，本步不改，下一步作为小改动处理。
- `apps/api/app/config.py` 中的默认 `app_name`：属于后端代码，本步不改。
- `apps/api/app/schemas/*` 中的字段描述：属于后端代码，本步不改。
- `apps/web/src/App.tsx` 中的下载文件名前缀：属于前端代码，本步不改。
- API 路径、Python module、前端 package name、导入路径和测试结构：没有完整评估前不做全局替换。

## 5. 当前建议

当前不应该把所有 ManJuFlow / 漫剧流 / manjuflow 一次性全部替换为 Dramora。原因是这些残留属于不同层级：

- README 中的 ManJuFlow 是早期代号解释，可以保留。
- 历史阶段文档中的 ManJuFlow 是开发记录，可以保留。
- `apps/web/index.html`、演示材料、当前市场试用说明属于用户可见层，应优先改。
- `apps/web/package.json` 中的 `manjuflow-web` 建议后续单独修改前端 package display name，并同步 package lock、运行前端构建。
- 后端 FastAPI title、config 默认 app name、schema 描述建议后续单独修改并运行后端测试。
- scripts 输出文案可以单独改，风险较低，但仍应作为独立步骤处理。

本次审计结论：品牌统一应按“用户可见层 -> 当前开发入口 -> package / app metadata -> 历史文档保留”的顺序推进。

## 6. 后续步骤

- 第 208 步：修复必须修改的品牌残留；
- 第 209 步：评估 package.json 显示名是否从 `manjuflow-web` 改为 `dramora-web`；
- 第 210 步：统一 scripts 输出文案；
- 第 211 步：保留历史文档，不再追求零残留。
