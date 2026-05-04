# Frontend CreationHome Refactor Plan｜前端 CreationHome 拆分计划

## 1. 背景与目标

`CreationHome.tsx` 已经从三入口工作台入口，逐步承担了剧本创作、文本改编、模型选择、文档导入预览和结果展示等多项职责。随着后续继续接入在线编辑、Word 导出、AI 编剧助手、质量评审和“短剧剧本 → 分镜 → Prompt”链路，如果继续把新增能力堆在同一个文件里，专业技术评审时会很难判断边界，也会增加后续交接和维护成本。

本计划的目标是为 `CreationHome` 制定小步拆分路径：

- 保持当前三入口真实 LLM 生成与改编链路稳定；
- 先拆边界清楚的 UI 和状态逻辑；
- 不为了重构而重写页面；
- 每一步都必须可构建、可回归、可回滚；
- 在进入在线编辑和导出闭环前，先把最近膨胀最快的文档导入与表单状态拆出去。

## 2. 当前 CreationHome 职责清单

当前 `CreationHome.tsx` 承担的职责包括：

- 三入口选择状态：灵感生成、电影剧本改编、小说 / 网文改编；
- 三入口草稿表单：项目标题、灵感文本、来源标题、待改编文本、改编方向、集数、额外要求；
- 创作模型选择：维护当前选择的 DeepSeek / Mimo / Kimi / MiniMax / 系统默认模型；
- 生成短剧剧本调用：构造请求、调用 `generateShortDramaScript`、处理 loading 和错误；
- 文档导入预览状态：按 film_script / novel 保存文件名、导入文本、预览结果、错误和 loading；
- 文档导入确认动作：填入、追加、取消；
- 结果展示：将 `ShortDramaScriptOutput` 传入统一结果组件；
- 下载入口提示与操作：复制 JSON、下载 JSON、下载 TXT、Word 导出状态提示；
- 错误与 loading 状态：生成错误、导入预览错误、按钮禁用状态；
- 页面文案和局部布局：入口卡片、表单、提示、结果区组合。

这些职责本身都合理，但不应长期集中在一个页面组件里。

## 3. 建议目标结构

建议目标结构如下：

```text
apps/web/src/components/creation/
├── CreationHome.tsx
├── CreationEntryCard.tsx
├── CreationEntryModal.tsx
├── CreationDraftForms.tsx
├── IdeaDraftForm.tsx
├── AdaptationDraftForm.tsx
├── DocumentImportPanel.tsx
├── ShortDramaScriptResult.tsx
└── CreationResultActions.tsx
```

```text
apps/web/src/hooks/creation/
├── useCreationDrafts.ts
├── useDocumentImportDrafts.ts
└── useShortDramaGeneration.ts
```

```text
apps/web/src/utils/creation/
├── creationPayloadBuilders.ts
└── creationDownloadUtils.ts
```

```text
apps/web/src/types/
├── scriptGeneration.ts
└── documentImport.ts
```

说明：

- `CreationHome.tsx` 保留为页面编排组件，负责组合入口、表单、模型选择和结果区；
- `CreationDraftForms.tsx` 负责根据当前入口选择渲染对应表单；
- `IdeaDraftForm.tsx` 只处理灵感生成表单；
- `AdaptationDraftForm.tsx` 复用电影剧本改编和小说 / 网文改编的通用字段；
- `DocumentImportPanel.tsx` 只处理导入预览 UI 和 fill / append / cancel 事件；
- `CreationResultActions.tsx` 后续可承载复制、下载、导出、继续编辑等结果操作；
- `useCreationDrafts.ts` 管理三入口草稿状态；
- `useDocumentImportDrafts.ts` 管理 film_script / novel 各自独立的导入预览状态；
- `useShortDramaGeneration.ts` 管理请求构造、调用、loading、错误和结果写入；
- `creationPayloadBuilders.ts` 收拢请求构造和入口映射；
- `creationDownloadUtils.ts` 收拢 JSON / TXT / 后续 Word 导出辅助逻辑。

这只是目标结构，不要求一次性完成。每一步只拆一个清晰边界，避免大爆炸式重构。

## 4. 拆分优先级

建议顺序：

1. 第 247 步：拆 `DocumentImportPanel`
2. 第 248 步：拆 `useDocumentImportDrafts` hook
3. 第 249 步：拆 `IdeaDraftForm` / `AdaptationDraftForm`
4. 第 250 步：拆 `useCreationDrafts` hook
5. 第 251 步：拆 generation payload builder
6. 第 252 步：再进入 `ShortDramaScriptResult` 在线编辑

如果在线编辑比结构治理更急，也建议至少先完成第 247 步，把 `DocumentImportPanel` 从 `CreationHome` 拆出去。文档导入是最近新增且边界清楚的模块，先拆它可以降低后续在线编辑继续堆叠的风险。

## 5. 每步验收标准

每次拆分都必须满足：

- `npm run build` 通过；
- `npm run test:e2e` 通过；
- 不改变页面文案；
- 不改变用户行为；
- 不改变后端 API 契约；
- 不改变 `ShortDramaGenerationInput` / `ShortDramaScriptOutput` 字段；
- `git diff` 范围清晰，能看出只是拆分或迁移；
- 不一次性移动太多文件；
- 如有行为风险，优先补自动化 smoke/e2e 覆盖。

## 6. 不做事项

本轮 CreationHome 拆分不做：

- 不趁机重写整个前端；
- 不引入 Redux / Zustand 等状态库；
- 不引入新的 UI 框架；
- 不改变后端契约；
- 不改 API 字段；
- 不删除已通过测试的功能；
- 不把三入口工作台拆成三个完全重复页面；
- 不把文档上传、剧本生成、结果编辑混成一个新大组件；
- 不做大爆炸式重构。

## 7. 后续 README / GitHub 主页同步提醒

当在线编辑 + Word 导入 / 导出闭环完成后，应更新：

- `README.md`
- `README.zh-CN.md`
- `README.en.md`

更新重点应突出 Dramora 当前定位：

> 三入口短剧剧本生成与改编工作台。

届时 README 可以说明：

- 灵感生成短剧剧本；
- 电影剧本改编短剧本；
- 小说 / 网文改编短剧本；
- 统一创作模型选择；
- 统一结果展示；
- Word 导入预览与导出闭环；
- 后续进入“短剧剧本 → 分镜 → Prompt”。

README 同步应放在功能闭环稳定之后，不在当前结构拆分步骤中顺手修改。

## 8. 当前建议下一步

建议第 247 步先拆 `DocumentImportPanel`。

原因：

- 它是最近新增的 UI 模块；
- 它与 `CreationHome` 的主生成逻辑边界清楚；
- 它只服务 film_script / novel 两个入口；
- 它已经具备独立的输入、预览、错误、loading 和确认动作；
- 拆分后可以显著降低 `CreationHome` 的阅读成本；
- 后续接真实 Word 上传时也能直接复用该组件。

第 247 步只应拆 UI 组件，不应同时改 API、不应接 multipart、不应调整后端逻辑。
