# Word Import Contract Design｜Word 文档导入契约设计

## 1. 目标

本文档用于定义 Dramora 真实 Word 文档导入的前后端契约，确保后续后端上传、前端预览、文件安全、改编方向字段和三入口剧本生成逻辑使用同一套规则。

目标不是“上传后自动改编”，而是：

```text
上传 Word
-> 提取文本
-> 展示导入预览
-> 用户确认填入 / 追加 / 取消
-> 用户填写改编方向
-> 使用所选创作模型生成或整理
```

Word 导入只负责把文档内容带入 Dramora。是否改成都市复仇、女性成长、悬疑反转、家庭伦理、职场逆袭或其他短剧方向，必须由用户确认或填写。

## 2. 产品交互原则

- Word 文件负责提供原文内容；
- 改编方向必须由用户确认或填写；
- 上传后不直接覆盖用户正在编辑的文本；
- 系统先展示导入预览；
- 用户选择：
  - 填入待改编文本；
  - 追加到当前文本后；
  - 取消导入；
- 用户仍需填写“改编方向 / 重点要求”。

不自动覆盖文本的原因：

- 防止误操作；
- 用户可能已手动编辑一部分；
- 同一份文本可改成不同短剧方向；
- 改编权和内容质量需要人工确认。

## 3. 支持文件类型

第一版只支持：

- `.docx`

暂不支持：

- `.doc`
- `pdf`
- 图片 OCR
- 压缩包
- 多文件批量上传

后续可扩展到 TXT / Markdown / PDF / OCR，但第一版应优先保证 `.docx` 解析、预览、确认和安全边界稳定。

## 4. 文件安全边界

- 限制文件大小，例如 10MB，后续可通过配置调整；
- 校验扩展名和 MIME；
- 清洗文件名，避免路径穿越、特殊字符和可执行文件伪装；
- 不直接公开上传文件 URL；
- 上传文件不进入 Git；
- 上传目录加入 `.gitignore`；
- 临时文件应可清理；
- 不在日志中记录完整剧本内容；
- 不把真实客户剧本提交公开仓库；
- 响应中不返回本机绝对路径，例如 `/Users/...`；
- metadata 只记录轻量追踪字段，例如 `source_id`、`storage_key`、文件大小、content type、提取状态和 warning。

建议上传目录延续现有安全审计方向，例如 `storage/uploads/` 或 `apps/api/storage/uploads/`，并保持公开仓库只提交目录说明或 `.gitkeep`，不提交真实文件。

## 5. 后端 API 设计建议

建议新增或升级接口：

```text
POST /api/uploads/script-file
```

请求：

```text
multipart/form-data
```

字段建议：

- `file: UploadFile`
- `project_title?: string`
- `source_type?: "film_script" | "novel" | "long_text" | "unknown"`
- `workspace_id?: string`
- `project_id?: string`
- `user_id?: string`
- `session_id?: string`

响应建议：

- `DocumentImportOutput`
- 或更聚焦的 `ScriptFileImportOutput`

字段建议：

- `source_id`
- `original_filename`
- `stored_filename` 或 `storage_key`
- `content_type`
- `file_size_bytes`
- `extracted_text`
- `extracted_text_length`
- `truncated`
- `warnings`
- `metadata`

注意：

- 不要在公开响应中返回本机绝对路径；
- 如果存储路径需要返回，返回 `storage_key`，而不是 `/Users/...` 绝对路径；
- `extracted_text` 可用于前端导入预览；
- 后续真实生产中可只返回摘要和 `source_id`，按需读取文本；
- 第一版内部试用可以返回 `extracted_text`，但日志和测试样例不得保存真实客户内容。

## 6. 后端 Schema 建议

建议新增：

- `ScriptFileImportInput`，如 multipart 之外仍需要结构化 metadata；
- `ScriptFileImportOutput`；
- `ImportedDocumentPreview`；
- `DocumentImportWarning`。

与现有 `upload.py` 的关系：

- 当前 `apps/api/app/schemas/upload.py` 是 JSON metadata-only / 早期文档导入 mock；
- 当前 `/api/uploads/script` 不接收真实 multipart 文件；
- 后续真实 multipart 上传建议使用单独 endpoint；
- 不建议破坏现有 `/api/uploads/script`，避免测试和旧前端逻辑断裂；
- 可以让 `/api/uploads/script-file` 作为真实 `.docx` 导入入口，旧 mock endpoint 保留为开发和兼容路径。

## 7. 前端交互契约

前端消费响应的流程：

- 用户点击“上传 Word 文档”；
- 上传成功后不直接覆盖文本框；
- 将 `extracted_text` 存入 `pendingImportedText` / `importPreview`；
- 展示：
  - 文件名；
  - 字数；
  - 是否截断；
  - warnings；
  - 前若干字符预览；
- 用户点击：
  - 填入待改编文本；
  - 追加到当前文本后；
  - 取消导入。

前端当前已有“导入预览 + 用户确认”的交互方向，后续真实接口接入时应复用这个产品逻辑，不应回退为上传后直接覆盖文本。

## 8. 与三入口剧本创作的关系

- 在 `CreationHome` 的电影剧本改编 / 小说网文改编中，Word 导入内容进入 `sourceText`；
- `sourceTitle` 可由 `original_filename` 或用户输入决定；
- `focus` / 改编方向仍由用户填写；
- `POST /api/scripts/generate-from-source` 继续消费 `ShortDramaGenerationInput`；
- Word 导入不直接调用 LLM；
- Word 导入不决定 `source_mode` 的创作意图，只提供原文内容和导入 metadata。

推荐映射：

| 导入响应字段 | CreationHome 字段 | 说明 |
| --- | --- | --- |
| `extracted_text` | `sourceText` | 用户确认后填入或追加 |
| `original_filename` | `sourceTitle` | 可作为默认标题，用户可修改 |
| `source_type` | `source_mode` 辅助选择 | 前端可辅助切换 film_script / novel，但不强制 |
| `warnings` | 导入预览提示 | 不阻断但需要可见 |
| `source_id` | metadata | 后续追踪来源 |

## 9. 与剧本改编 / 分镜工作区的关系

- `ScriptSegmentationWorkspace` 可复用同一 `DocumentImportOutput`；
- 导入文本可进入“待改编文本”；
- 后续再进入“剧本 -> 分镜 -> Prompt”；
- 不应把文档上传逻辑重复写在多个页面；
- 前端可抽 `DocumentImportPanel` 组件，后续被 `CreationHome` 和 `ScriptSegmentationWorkspace` 复用；
- 文档上传、预览、确认、warning 展示应由组件统一处理；
- 各业务页面只负责把确认后的文本接入自己的输入字段。

## 10. 推荐文件结构

后端：

- `apps/api/app/schemas/document_import.py` 或在 `upload.py` 中新增类型；
- `apps/api/app/services/document_import_service.py`；
- `apps/api/app/routers/uploads.py`；
- `tests/api/test_document_import_schema.py`；
- `tests/api/test_document_import_service.py`；
- `tests/api/test_document_import_endpoint.py`。

前端：

- `apps/web/src/types/documentImport.ts`；
- `apps/web/src/api/documentImports.ts`；
- `apps/web/src/components/document/DocumentImportPanel.tsx`；
- `CreationHome` / `ScriptSegmentationWorkspace` 复用该组件。

## 11. 依赖计划

后续代码步骤中再接：

- `python-multipart`
- `python-docx`

当前文档不改 `requirements.txt`，不新增依赖，不实现真实解析。

## 12. 测试计划

后续测试应覆盖：

- `.docx` 文件能解析；
- 非 docx 拒绝；
- 超大文件拒绝；
- 文件名清洗；
- 空文档处理；
- 提取文本过长截断；
- endpoint 不返回本机绝对路径；
- 上传文件不进入 Git；
- 日志不记录完整剧本内容；
- 前端导入预览不自动覆盖文本；
- 填入 / 追加 / 取消行为正确；
- warnings 能在前端预览卡片展示。

## 13. 后续步骤

- 第 236 步：后端 document import schema；
- 第 237 步：`python-multipart` / `python-docx` 依赖与 service；
- 第 238 步：真实 multipart endpoint；
- 第 239 步：前端 `DocumentImportPanel`；
- 第 240 步：`CreationHome` 接真实 Word 导入；
- 第 241 步：`ScriptSegmentationWorkspace` 复用 `DocumentImportPanel`。
