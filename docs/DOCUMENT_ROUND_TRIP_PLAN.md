# Document Round-trip Plan｜文档往返编辑方案

## 1. 文档目的

本文档用于定义 ManJuFlow 后续如何支持编剧用户熟悉的文档往返工作流：

- 在线编辑；
- 下载 Word；
- 离线编辑；
- 再上传；
- 继续进入剧本切分、分镜、绘图 / 媒体 Prompt 等后续阶段。

这不是锦上添花功能，而是编剧行业用户的核心工作习惯。ManJuFlow 后续不能只支持单向生成，还需要让生成结果可编辑、可导出、可再导入，并能继续进入下一步生产链路。

当前文档只做方案设计，不实现代码，不接真实文件处理，不引入新依赖。

## 2. 用户真实需求

编剧、短剧策划、导演和内容团队在实际工作中可能需要：

- AI 生成剧本后，由编剧在线修改；
- 下载 Word 给团队审稿、批注或归档；
- 离线修改后重新上传到系统继续使用；
- 对已有剧本直接上传，进入切分和分镜链路；
- 对分镜表、Prompt 表下载后修改；
- 在任意阶段重新导入修改版，并继续后续工作流。

因此，ManJuFlow 后续需要支持“生成结果 → 人工编辑 → 文档导出 → 离线修改 → 再导入 → 继续生成”的闭环。

## 3. 支持阶段范围

未来应支持文档往返的阶段包括：

- `ScriptOutput`：结构化剧本；
- `Script Segmentation`：已有剧本切分结果；
- `StoryboardOutput`：分镜表；
- `ImagePromptOutput`：绘图 / 媒体提示词；
- Assistant 改写结果；
- 后续可扩展到角色设定、分集大纲、场景表。

第一版不必一次覆盖全部阶段。建议优先从以下阶段开始：

- Script；
- Existing Script；
- Storyboard。

这些阶段最贴近编剧和内容团队的真实编辑习惯，也最适合市场试用前验证。

## 4. 第一版能力边界

第一版建议保持克制，优先跑通主流程：

- 在线编辑先支持纯文本 / 结构化文本，不做复杂富文本；
- Word 下载先支持 `.docx`，如实现成本较高，可先提供 Markdown / TXT fallback；
- Word 上传先支持 `.docx` 提取纯文本；
- 上传后先进入对应阶段输入框，由用户确认后继续下一步；
- 不做多人实时协作；
- 不做复杂版本比较；
- 不做复杂排版还原；
- 不保存真实客户文件到公开仓库。

第一版目标是让用户能把内容拿出来、改完再放回来，而不是一次性实现完整在线文档协作系统。

## 5. Document Export 设计

文档导出能力用于把当前阶段结果转成可下载文件。

可导出格式：

- `.docx`；
- `.txt`；
- `.json`；
- 后续可选 `.md`。

导出对象：

- 剧本；
- 切分结果；
- 分镜；
- Prompt；
- Assistant 改写结果。

建议后端后续新增：

- `DocumentExportInput`；
- `DocumentExportOutput`；
- `POST /api/documents/export`。

`DocumentExportInput` 字段建议：

- `project_title`；
- `document_type`；
- `source_stage`；
- `content_text`；
- `structured_payload`；
- `export_format`；
- `filename`；
- `metadata`。

导出服务需要保证：

- 不把临时导出文件提交到 Git；
- 不泄露真实客户内容到公开样例；
- 导出内容可追溯到项目、workspace 和来源阶段；
- JSON 导出保留原始字段名，Word / TXT 导出面向非技术用户可读。

## 6. Document Import 设计

文档导入能力用于把用户离线修改后的内容重新带回系统。

可导入：

- 用户已有剧本 Word；
- 用户修改后的剧本 Word；
- 用户修改后的分镜 Word；
- 用户修改后的 Prompt Word；
- 后续支持 `.txt` / `.md`。

建议后端后续新增：

- `DocumentImportInput`；
- `DocumentImportOutput`；
- `POST /api/documents/import`。

`DocumentImportInput` / `DocumentImportOutput` 字段建议：

- `project_title`；
- `source_stage`；
- `target_stage`；
- `file_name`；
- `file_size`；
- `mime_type`；
- `extracted_text`；
- `source_id`；
- `workspace_id`；
- `project_id`；
- `session_id`；
- `metadata`。

导入后不应让前端依赖后端本地文件路径。前端应使用 `source_id`、`extracted_text` 和结构化 metadata 继续工作。

## 7. 任意阶段上传的路由策略

用户可能在不同阶段上传文件，因此上传能力不应长期只绑定到 `/api/uploads/script`。

未来建议抽象为：

- `POST /api/documents/import`；
- `POST /api/documents/export`。

现有接口：

- `/api/uploads/script` 继续作为第五阶段已有剧本 mock 上传兼容接口。

未来迁移策略：

- script upload 可以迁移到 document import；
- 或由 `/api/uploads/script` 内部包装 `/api/documents/import`；
- 前端逐步从“已有剧本上传”扩展为“任意阶段导入文档”。

这样可以避免后续为每个阶段单独新增一套上传接口。

## 8. 在线编辑器策略

第一版在线编辑器不做复杂富文本。

建议：

- 使用 textarea / plain text editor；
- 结构化 JSON 可继续保留；
- 用户编辑文本版后可重新带入下一步；
- 每个编辑区接入 `CharacterCountHint`；
- 超限时禁止继续生成；
- 编辑后标记 dirty state；
- 用户离开前提示是否保存。

在线编辑区需要服务编剧工作流，而不是替代专业文档编辑器。复杂排版、批注、多人协作可以放到后续阶段。

## 9. 版本与回溯策略

后续需要记录文档修改链路，避免离线修改后来源不清。

建议记录：

- `source_id`；
- `version_id`；
- `parent_version_id`；
- `edited_by`；
- `created_at`；
- `source_stage`；
- `target_stage`；
- `checksum` 或 `content_hash`；
- `metadata`。

第一版可以先做 mock / metadata-only。进入市场试用或私有部署前，再逐步引入 SQLite 持久化。

版本链路应回答：

- 这份文本来自哪个阶段；
- 谁编辑过；
- 是否从 Word 再上传；
- 当前版本能否继续生成分镜或 Prompt；
- 是否可以追溯到上一版。

## 10. 文件保存策略

文件保存必须遵守公开仓库安全边界。

建议：

- 真实上传文件不进入 Git；
- 上传目录进入 `.gitignore`；
- 第一版可放 `storage/uploads` 或 `data/uploads`；
- 后续用 SQLite 记录 metadata；
- 文件清理策略必须明确；
- 公开仓库只放目录说明和 `.gitkeep`；
- 不保存真实客户剧本到公开仓库。

未来私有部署可以迁移到对象存储或私有文件服务，但公开仓库只保留抽象接口、mock 示例和安全说明。

## 11. 字数上限与安全

Document Round-trip 必须复用输入上限策略。

要求：

- 上传后的 `extracted_text` 也要走 100,000 字符限制；
- 在线编辑区也要接入 `CharacterCountHint`；
- 后端必须校验；
- 不在日志中打印完整剧本；
- Word 文件大小第一版建议限制为 10 MB；
- 不允许上传可执行文件；
- 后续需要 MIME / 扩展名检查。

需要再次强调：100,000 字符是 UI / 输入保存上限，不是单次 LLM 调用上限。真实 LLM 处理长文档时仍必须分块。

## 12. 用户体验流程

### 流程 A：AI 生成剧本后在线编辑

AI 生成剧本
→ 用户在线编辑文本
→ 字数检测通过
→ 用户确认
→ 继续生成分镜

### 流程 B：AI 生成剧本后离线修改

AI 生成剧本
→ 下载 Word
→ 编剧离线修改
→ 上传 Word
→ 提取文本
→ 重新切分 / 生成分镜

### 流程 C：已有剧本 Word 进入工作流

已有剧本 Word
→ 上传
→ 提取文本
→ 剧本切分
→ 分镜
→ 绘图 / 媒体 Prompt

### 流程 D：分镜表离线修改后继续生成 Prompt

分镜表
→ 下载 Word
→ 导演或策划修改
→ 上传修改版
→ 提取文本 / 结构化解析
→ 继续生成 Prompt

## 13. 市场试用优先级

### P0

- 在线编辑文本；
- 字数限制；
- 下载 `.txt` / `.json`；
- 真实 `.docx` 上传提取文本；
- 上传后进入已有剧本切分。

### P1

- 下载 `.docx`；
- 分镜 / Prompt 下载 Word；
- 上传后选择目标阶段；
- metadata 保存。

### P2

- 版本管理；
- 文档比对；
- 多人协作；
- 审批流。

市场试用前优先完成 P0。P1 和 P2 应在真实用户反馈后再逐步推进。

## 14. 后续小闭环建议

建议后续按以下小闭环推进：

- 新增 Document Round-trip 方案文档；
- 新增 `DocumentExport` Schema；
- 新增纯文本导出服务；
- 新增 `.docx` 导出服务；
- 新增 `DocumentImport` Schema；
- 新增真实 multipart upload；
- 接入 `python-docx`；
- 上传后 `extracted_text` 进入切分；
- 在线编辑区第一版；
- 浏览器验收。

每一步都应保持可测试、可回滚，不一次性重构上传、导出、编辑和版本管理。

## 15. 第 179 步验收标准

- `docs/DOCUMENT_ROUND_TRIP_PLAN.md` 已新增；
- 文档明确在线编辑 / Word 下载 / 再上传需求；
- 文档说明任意阶段可能上传；
- 文档提出 `DocumentImport` / `DocumentExport` 抽象；
- 文档明确第一版能力边界；
- 文档明确文件保存与安全策略；
- 文档明确字数上限；
- 文档不包含敏感信息；
- 不修改代码。
