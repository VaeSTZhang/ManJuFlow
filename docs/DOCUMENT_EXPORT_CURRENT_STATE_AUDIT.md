# Document Export Current State Audit｜文档导出当前状态审计

## 1. 审计目标

本审计用于确认 Dramora 进入 Document Export / Word 导出闭环前的现状，避免重复开发、不必要依赖和一次性过大的 DOCX 接入。

当前目标不是直接接入 Word 导出，而是先确认：

- 已有哪些 schema / 测试 / 前端下载能力；
- 后端是否已有导出 service 和 endpoint；
- 编辑稿 `effectiveScript` 如何进入导出链路；
- TXT / JSON / DOCX 应按什么顺序小步实现；
- 导出过程如何避免 API Key、本机路径、真实客户内容或真实剧本进入仓库。

## 2. 当前已具备能力

### 后端 Document Export Schema

当前已存在：

- `apps/api/app/schemas/document.py`
  - `DocumentExportFormat = Literal["txt", "json", "docx"]`
  - `DocumentSourceStage`
  - `DocumentExportInput`
  - `DocumentExportOutput`
- `apps/api/app/schemas/__init__.py`
  - 已导出 `DocumentExportInput` / `DocumentExportOutput`

`DocumentExportInput` 当前支持：

- `project_title`
- `document_type`
- `source_stage`
- `content_text`
- `structured_payload`
- `export_format`
- `filename`
- `workspace_id`
- `project_id`
- `session_id`
- `metadata`

`DocumentExportOutput` 当前支持：

- `project_title`
- `document_type`
- `source_stage`
- `export_format`
- `filename`
- `content_text`
- `download_url`
- `file_size_bytes`
- `workspace_id`
- `project_id`
- `session_id`
- `metadata`

### 支持格式

Schema 层已声明支持：

- `txt`
- `json`
- `docx`

这只是契约层支持，不代表当前已有真实 DOCX 生成 service。

### 测试

当前已存在：

- `tests/api/test_document_schema.py`

覆盖内容包括：

- `DocumentExportInput` 可用纯文本创建；
- `DocumentExportInput` 可用结构化 payload 创建；
- `txt` / `json` / `docx` 格式校验；
- `script` / `storyboard` / `image_prompt` 来源阶段校验；
- `metadata` 默认 dict 互不污染；
- `DocumentExportOutput` 可创建并 `model_dump`；
- 非法 `export_format` / `source_stage` 会校验失败。

### Document Import Preview

导入侧已经完成一条 JSON preview 小闭环：

- `apps/api/app/schemas/document_import.py`
  - `DocumentImportPreviewRequest`
  - `DocumentImportSource`
  - `DocumentImportPreview`
  - `DocumentImportAction`
  - `DocumentImportOutput`
  - `DocumentImportError`
- `apps/api/app/services/document_import_service.py`
  - 文本归一化；
  - 预览文本截断；
  - 段落数量估算；
  - 标题识别；
  - 安全文件名清洗；
  - `DocumentImportOutput` 构造。
- `apps/api/app/routers/documents.py`
  - `POST /api/documents/import-preview`

导入侧当前仍不是最终真实 `.docx` multipart 上传接口，但已经验证了“导入预览 + 用户确认填入 / 追加 / 取消”的契约。

### 前端当前下载能力

`CreationHome` 当前已有浏览器本地下载能力：

- 复制 JSON：
  - 使用 `navigator.clipboard.writeText(JSON.stringify(effectiveScript, null, 2))`
- 下载 JSON：
  - 使用浏览器 `Blob` + `<a download>`；
  - 文件名：`dramora-short-drama-script.json`
- 下载 TXT：
  - 使用浏览器 `Blob` + `<a download>`；
  - 文件名：`dramora-short-drama-script.txt`
  - 文本由 `formatShortDramaScriptTxt(...)` 生成。
- Word 下载：
  - `ShortDramaScriptResult` 已有 `onDownloadDocx` prop；
  - 当前未传入真实 handler；
  - UI 显示“Word 导出将在文档导出闭环接入”。

前端 JSON / TXT 当前已经使用 `effectiveScript`，即：

```text
editableScript ?? generatedScript
```

这意味着在线编辑后的基础信息、角色字段、分集字段已经进入现有 JSON / TXT 导出。

## 3. 当前缺口

### 后端缺口

当前尚未发现：

- `document_export_service.py`；
- `POST /api/documents/export`；
- 真实 DOCX 生成逻辑；
- TXT / JSON 后端导出 service；
- 导出内容安全清洗 service；
- 导出文件名统一生成策略；
- 导出结果 metadata 规范化；
- 导出 endpoint 测试；
- DOCX service 测试。

### 前端缺口

当前尚未发现：

- `apps/web/src/types/documentExport.ts`；
- `apps/web/src/api/documentExport.ts`；
- 前端调用后端 document export endpoint；
- Word 下载真实接入；
- 后端导出错误处理；
- 后端导出 metadata 传递；
- 编辑稿 `effectiveScript` 通过 API 交给后端导出。

### DOCX 缺口

当前尚未接入：

- `python-docx`；
- DOCX 模板；
- DOCX 段落样式；
- DOCX 响应流；
- DOCX 临时文件安全策略；
- DOCX 生成测试；
- 前端 Word 下载 e2e。

### 测试缺口

当前已有 schema 测试和前端 JSON / TXT e2e，但缺少：

- `DocumentExport` service 单元测试；
- `POST /api/documents/export` endpoint 测试；
- TXT / JSON 导出结果内容测试；
- DOCX service 测试；
- DOCX endpoint 测试；
- 编辑后 Word 导出 e2e；
- 后端导出不返回本机绝对路径的测试；
- 导出 metadata 不包含 API Key / 本机路径 / 敏感内容的测试。

## 4. TXT / JSON / DOCX 建议路线

建议按以下顺序推进，不要把 DOCX、endpoint、前端 Word 下载混在同一个大步骤里：

1. 后端 service 支持 TXT / JSON 字符串生成；
2. 为 TXT / JSON service 补单元测试；
3. 新增 `POST /api/documents/export` endpoint；
4. 新增前端 `documentExport` types / api；
5. 前端将 `effectiveScript` 传给后端导出 TXT / JSON；
6. 单独评估并接入 DOCX service；
7. 再接前端 Word 下载；
8. 最后补编辑后 Word / TXT / JSON 导出 e2e。

这样可以先把“当前有效稿 → 后端导出契约 → 可测试响应”跑通，再进入 DOCX 依赖和真实文件响应。

## 5. DOCX 依赖评估

`python-docx` 是合理候选，但不应在下一步直接引入。

引入前需要确认：

- 项目依赖管理是 `requirements.txt`、`pyproject.toml`，还是其他方式；
- 后端测试环境是否能稳定安装；
- DOCX 是否只需要基础段落和标题样式；
- 是否需要中文字体或复杂模板；
- 是否需要保留场景 / 对白层级；
- 是否需要生成临时文件，还是可以直接响应 bytes。

DOCX 导出安全要求：

- 不提交生成的真实 `.docx`；
- 不把真实客户剧本写入测试 fixture；
- 不返回本机绝对路径；
- 不写死 `/Users/...` 这类本机路径；
- 如果需要临时文件，只写入安全临时目录；
- 响应应使用安全文件名；
- 日志不记录完整剧本文本；
- 测试使用安全虚构内容。

## 6. effectiveScript 导出原则

前端导出应继续使用当前有效稿：

```text
editableScript ?? generatedScript
```

后端不应判断前端编辑历史，也不应试图重建 AI 原始稿和用户编辑稿之间的 diff。后端只接收“当前要导出的稿件”。

建议前端传入导出 metadata：

- `edited: true | false`
- `source_mode`
- `provider`
- `model`
- `generated_at`
- `last_edited_at`
- `exported_from: "creation_home"`

后端可在 `DocumentExportOutput.metadata` 中保留安全追踪字段，例如：

- `export_format`
- `source_stage`
- `content_source`
- `edited`
- `generated_at`
- `last_edited_at`

必须禁止记录：

- API Key；
- `.env` 内容；
- 本机绝对路径；
- 完整服务器路径；
- 真实客户内容；
- 真实合作方敏感信息。

## 7. 建议后续小步

建议后续顺序：

1. 第 276 步：Document Export service 支持 TXT / JSON
2. 第 277 步：Document Export service 单元测试
3. 第 278 步：Document Export endpoint
4. 第 279 步：前端 documentExport types / api
5. 第 280 步：前端接入后端 TXT / JSON 导出
6. 第 281 步：DOCX 依赖评估与 service
7. 第 282 步：DOCX endpoint / 前端 Word 下载
8. 第 283 步：e2e 覆盖编辑后导出

每一步都应保持：

- 改动范围小；
- 测试可独立运行；
- 不提交真实文件；
- 不引入不必要依赖；
- 不让 `CreationHome` 或 `ShortDramaScriptResult` 重新膨胀。

## 8. 当前建议结论

当前结论：

- 下一步不直接做 DOCX；
- 先复用已有 `DocumentExportInput` / `DocumentExportOutput`；
- 先新增后端 TXT / JSON export service；
- 再补 endpoint；
- 再接前端 API；
- DOCX 单独做依赖评估和小闭环；
- 导出链路必须可测试、可替换、无敏感文件落仓库。

当前最稳妥的下一步是：

```text
第 276 步：Document Export service 支持 TXT / JSON
```

这一步应只做后端 service 和单元测试，不接 DOCX，不接 endpoint，不改前端。
