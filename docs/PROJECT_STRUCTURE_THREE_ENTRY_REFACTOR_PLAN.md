# Project Structure Refactor Plan for Three-entry Script Workbench｜三入口短剧工作台项目结构重整方案

> 当前状态：老板已取消当前版本的右侧 AI 聊天界面、AI Assistant、`/api/assistant/chat` 和 `suggested_actions`。本文中关于 assistant schema / service / router / panel 的内容仅作为历史结构方案归档，不纳入当前实施路线。三入口结构治理继续保留，但重点改为剧本生成、改编、在线编辑、导入导出、用量记录、质量评审和后续分镜 / Prompt 工作流。

## 1. 文档目的

本文档用于规划 ManJuFlow 在“三入口短剧剧本生成与改编工作台”方向下的项目结构，避免需求继续变化时出现：

- 代码写死；
- 文件边界混乱；
- `App.tsx` 继续膨胀；
- 单个 service 承担过多职责；
- Prompt、Assistant、Document、后续分镜 / Prompt 链路互相缠绕。

当前产品主线已调整为：

1. 灵感生成短剧剧本；
2. 电影剧本改编短剧剧本；
3. 小说改编短剧剧本。

本计划的目标不是一次性大重构，而是先定义清晰边界，后续按小闭环逐步迁移。

## 2. 当前风险

随着第五阶段需求变化，当前结构存在以下风险：

- `App.tsx` 继续膨胀，所有 workspace、表单、结果展示、跳转逻辑都堆在一起；
- `script_service.py` 同时承担灵感生成、电影改编、小说改编，导致逻辑混杂；
- Prompt 文件命名和版本边界不清，后续容易把不同入口混用同一个 prompt；
- Assistant 和主生成链路混在一起，导致聊天建议、改写、正式生成职责不清；
- Document import / export 和 upload 混在一起，导致后续文件处理接口难扩展；
- 未来切分 / 分镜 / Prompt 链路与当前剧本生成主链路边界不清；
- 新增 source_mode 时需要改多个散落文件，容易返工；
- 前端多入口表单可能复制粘贴，形成多个难维护的重复页面。

这些风险会直接影响老板演示、市场试用、合作方技术评审和后续私有部署。

## 3. 后端推荐结构

后端建议逐步演进为以下结构：

```text
apps/api/app/
├── schemas/
│   ├── script.py
│   ├── script_generation.py
│   ├── adaptation.py
│   ├── document.py
│   └── assistant.py
├── services/
│   ├── script_generation/
│   │   ├── registry.py
│   │   ├── idea_generator.py
│   │   ├── film_adaptation.py
│   │   ├── novel_adaptation.py
│   │   └── shared.py
│   ├── assistant/
│   │   ├── assistant_service.py
│   │   └── suggested_actions.py
│   ├── documents/
│   │   ├── export_service.py
│   │   └── import_service.py
│   └── workflow/
│       └── next_step_mapper.py
├── prompts/
│   ├── idea_to_short_drama_script_v1.md
│   ├── film_script_to_short_drama_v1.md
│   ├── novel_to_short_drama_v1.md
│   └── assistant_script_rewrite_v1.md
└── routers/
    ├── scripts.py
    ├── assistant.py
    └── documents.py
```

说明：

- 不要一次性重构；
- 先从新增模块开始放到新结构；
- 老模块等功能稳定后再迁移；
- 每次迁移都必须有测试；
- 不为了目录整齐破坏现有可用链路。

### schemas

建议拆分：

- `script.py`：保留当前已有 ScriptOutput 相关结构；
- `script_generation.py`：三入口统一生成输入 / 输出协议；
- `adaptation.py`：电影剧本改编、小说改编等来源改编协议；
- `document.py`：DocumentImport / DocumentExport；
- `assistant.py`：Assistant Chat、suggested actions、context。

### services

`script_generation/` 应成为三入口主生成模块：

- `registry.py`：根据 source_mode 找到对应生成器；
- `idea_generator.py`：灵感生成短剧；
- `film_adaptation.py`：电影剧本改短剧；
- `novel_adaptation.py`：小说改短剧；
- `shared.py`：共用 formatter、mock helper、LLM 调用准备逻辑。

### routers

短期可继续复用 `routers/scripts.py`，但不应无限堆 endpoint。

后续可以评估：

- scripts router 保持主入口；
- assistant router 独立；
- documents router 独立。

## 4. source_mode 注册机制

建议定义 `source_mode`，用于描述短剧剧本生成来源：

- `idea`；
- `film_script`；
- `novel`；
- `assistant_rewrite`；
- `uploaded_document`。

每个 `source_mode` 应绑定：

- input schema；
- prompt template；
- mock generator；
- llm generator；
- frontend form；
- character limits；
- output mapper；
- next actions。

建议注册表结构包含：

- `source_mode`；
- `label`；
- `description`；
- `input_schema`；
- `prompt_version`；
- `mock_generator`；
- `llm_generator`；
- `max_input_chars`；
- `default_output_mapper`；
- `supported_next_actions`。

这样可以避免未来新增入口时到处改代码。例如后续新增“漫画大纲改短剧”，只需新增 source_mode 注册项、prompt、service、前端表单，而不是重写主流程。

## 5. Prompt 文件规则

Prompt 必须版本化，不应写死在 service 中。

建议命名：

- `idea_to_short_drama_script_v1.md`；
- `film_script_to_short_drama_v1.md`；
- `novel_to_short_drama_v1.md`；
- `assistant_rewrite_short_drama_v1.md`；
- `script_to_storyboard_v1.md`；
- `storyboard_to_image_prompt_v1.md`。

规则：

- 每个入口有独立 Prompt；
- Prompt 文件名包含任务方向和版本；
- LLM 调用记录 `source_mode` 和 `prompt_version`；
- 不同业务入口不能随意混用 prompt；
- Prompt 更新必须可追溯；
- Prompt 内不写 API Key、服务器地址、真实客户内容。

## 6. 前端推荐结构

前端建议逐步演进为：

```text
apps/web/src/
├── components/
│   ├── creation/
│   │   ├── CreationEntryModal.tsx
│   │   ├── CreationEntryCard.tsx
│   │   ├── IdeaToScriptForm.tsx
│   │   ├── FilmScriptAdaptationForm.tsx
│   │   ├── NovelAdaptationForm.tsx
│   │   └── ShortDramaScriptResult.tsx
│   ├── assistant/
│   │   ├── AssistantPanel.tsx
│   │   ├── AssistantMessageList.tsx
│   │   ├── AssistantComposer.tsx
│   │   └── AssistantSuggestedActions.tsx
│   ├── documents/
│   │   ├── DocumentExportButton.tsx
│   │   └── DocumentImportPanel.tsx
│   └── common/
│       └── CharacterCountHint.tsx
├── types/
│   ├── scriptGeneration.ts
│   ├── adaptation.ts
│   ├── assistant.ts
│   └── document.ts
├── api/
│   ├── scriptGeneration.ts
│   ├── assistant.ts
│   └── documents.ts
└── constants/
    └── creationEntryRegistry.ts
```

前端原则：

- `App.tsx` 只做组合和状态入口；
- 不继续把所有业务逻辑塞进 `App.tsx`；
- 三入口表单独立成组件；
- 入口卡片由 registry 驱动；
- CharacterCountHint 继续作为通用组件；
- Document import/export 独立组件；
- Assistant 独立面板，不塞进每个表单。

### creationEntryRegistry

建议前端注册表包含：

- `id`；
- `label`；
- `description`；
- `sourceMode`；
- `defaultWorkspace`；
- `formComponent`；
- `maxInputChars`；
- `nextActions`。

这样前端新增入口时，不需要大改页面结构。

## 7. AI Assistant 模块边界

Assistant 是独立能力，不是三入口表单的一部分。

Assistant 应具备：

- 独立 schema；
- 独立 service；
- 独立 endpoint；
- 独立 prompt；
- 独立 `ASSISTANT_GENERATION_MODE`；
- 可读取当前上下文；
- 只能通过 suggested_actions 影响主流程；
- 所有 suggested actions 需要用户确认。

Assistant 可支持：

- 改写当前剧本；
- 把小说段落改成短剧场景；
- 增强钩子；
- 生成下一集方向；
- 将结果带入三入口之一；
- 将当前短剧剧本带入后续切分 / 分镜 / Prompt。

边界要求：

- Assistant 不直接调用主生成 service 修改生产数据；
- Assistant 不自动跨项目读取上下文；
- Assistant 不与电影改编 / 小说改编共用业务 prompt；
- Assistant 的 UsageLedger 和主生成链路分开记录。

## 8. Document 模块边界

当前 `upload_service` 继续保留 mock upload 能力。

后续 document import/export 应独立为 documents 模块：

- `documents/export_service.py`；
- `documents/import_service.py`；
- `routers/documents.py`；
- `schemas/document.py`。

边界要求：

- 不把所有文件处理都塞进 `uploads.py`；
- `/api/uploads/script` 可作为现有兼容接口；
- 后续统一文档导入导出走 `/api/documents/import` 和 `/api/documents/export`；
- Document Round-trip 包括在线编辑、导出、上传、版本 metadata；
- 真实上传文件不进入 Git；
- 导出文件和上传文件必须有清理策略。

## 9. 下一大功能边界

短剧剧本生成之后的以下能力，是下一大功能预备：

- Script Segmentation；
- Storyboard；
- ImagePrompt；
- Media Prompt。

当前不要让这些能力抢主入口。

推荐产品关系：

短剧剧本生成 / 改编
→ 在线编辑 / 导出 / 上传
→ 继续进入切分
→ 分镜
→ Prompt
→ 后续媒体生成。

前端可以保留“继续进入下一步”按钮，但当前主页面应优先服务三入口短剧剧本工作台。

## 10. 分阶段迁移路线

建议路线：

- 第 182 步：结构重整方案；
- 第 183 步：更新市场试用方案和老板演示脚本；
- 第 184 步：新增三入口 Schema；
- 第 185 步：Prompt 文件规划；
- 第 186 步：前端入口选择 UI 设计；
- 第 187 步：抽出 `CreationEntryModal`；
- 第 188 步：电影改短剧 mock；
- 第 189 步：小说改短剧 mock；
- 第 190 步：Assistant 设计文档更新；
- 第 191 步：再进入代码重构。

迁移原则：

- 一次只迁移一个边界；
- 每步都要测试；
- 不为了结构重整破坏老板演示主链路；
- 优先让新增能力进入新结构，旧能力逐步迁移。

## 11. 验收标准

- 文档明确防写死原则；
- 文档明确后端结构；
- 文档明确前端结构；
- 文档明确 `source_mode` 注册机制；
- 文档明确 Prompt 命名规则；
- 文档明确 AI Assistant 边界；
- 文档明确 Document 边界；
- 文档明确下一大功能边界；
- 不修改代码；
- 不包含敏感信息。
