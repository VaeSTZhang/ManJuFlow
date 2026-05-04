# DOCX Export Implementation Plan｜Word 导出实现方案

## 1. 目标与范围

DOCX 导出的目标是让 Dramora 内部用户能够下载编辑后的短剧剧本 Word 文档，用于老板审看、团队流转、离线修改和归档。

第一版范围：

- 只支持 `ShortDramaScriptOutput`；
- 只支持 `source_stage="script"`；
- 导出前端当前有效稿，即 `editableScript ?? generatedScript`；
- 面向短剧剧本内容生成基础 Word 文档；
- 不支持复杂模板；
- 不支持封面图；
- 不支持批注；
- 不支持多人协作；
- 不支持云端保存；
- 不支持服务端版本库。

第一版重点是把“生成 → 在线编辑 → 下载 Word”打成稳定闭环，而不是一次性实现专业排版系统。

## 2. 依赖选择

建议评估并采用 `python-docx` 作为第一版 DOCX 导出依赖。

优点：

- 成熟、常用；
- 适合基础 Word 文档生成；
- API 简单，适合标题、段落、列表等基础结构；
- 不需要引入重型文档服务。

缺点：

- 复杂排版能力有限；
- 中文字体、字号和段落样式需要谨慎设置；
- 不适合复杂批注、修订痕迹、多人协作或高级模板；
- 对复杂表格和媒体内容需要额外设计。

当前建议：

- `python-docx` 可以作为第一版 DOCX 导出依赖；
- 依赖必须在单独小步骤引入；
- 必须加入项目现有后端依赖管理文件；
- 不允许随意散装安装；
- 引入后必须补 service 测试和 endpoint 测试。

## 3. 输出方式建议

DOCX 第一版建议后端生成 bytes，而不是长期落盘。

可选方案：

1. `BytesIO` 内存流
   - 推荐第一版使用；
   - 避免本机路径；
   - 避免真实文件落盘；
   - 适合单个剧本文档下载。
2. 临时安全目录
   - 适合后续大文件或复杂模板；
   - 必须使用安全临时目录；
   - 必须有清理策略；
   - 不返回本机绝对路径。

第一版优先采用 `BytesIO`，让 endpoint 直接返回 bytes。

## 4. 后端实现建议

建议新增独立 service 文件：

```text
apps/api/app/services/document_docx_export_service.py
```

不建议继续把 DOCX 逻辑塞进 `document_export_service.py`，避免 TXT / JSON service 和二进制文件生成逻辑混杂。

建议函数：

```python
build_docx_export_bytes(input_data: DocumentExportInput) -> bytes
build_short_drama_docx_document(...)
sanitize_docx_filename(...)
```

职责建议：

- `build_docx_export_bytes`
  - 接收 `DocumentExportInput`；
  - 校验 `export_format == "docx"`；
  - 根据 `structured_payload` 构建 Word 文档；
  - 返回 bytes；
  - 不写入长期文件。
- `build_short_drama_docx_document`
  - 负责把 `ShortDramaScriptOutput` 的关键字段写入 `python-docx` Document；
  - 保持基础标题、段落和列表结构；
  - 不做复杂模板。
- `sanitize_docx_filename`
  - 清洗文件名；
  - 去除路径分隔符；
  - 确保 `.docx` 后缀；
  - 不返回本机绝对路径。

## 5. Endpoint 策略

当前接口：

```text
POST /api/documents/export
```

返回 JSON `DocumentExportOutput`，适合 TXT / JSON 内容，不适合返回 DOCX bytes。

DOCX 文件下载有两个方案：

### 方案 A：继续使用 `/api/documents/export`

问题：

- JSON response 不适合二进制 bytes；
- base64 会增加体积和复杂度；
- 前端下载逻辑会变得含混；
- `DocumentExportOutput.content_text` 不适合承载 DOCX。

不推荐。

### 方案 B：新增专用文件下载 endpoint

建议新增：

```text
POST /api/documents/export-file
```

返回：

- `StreamingResponse` 或 `Response` bytes；
- `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`；
- `Content-Disposition: attachment; filename="..."`。

推荐采用方案 B。

理由：

- JSON 导出和文件导出边界清楚；
- 前端可以直接 `response.blob()`；
- 不把二进制塞进 JSON；
- 后续 PDF、ZIP 等文件导出也可复用同一思路。

## 6. 前端策略

前端建议新增：

```text
apps/web/src/api/documentExport.ts
```

在现有 `exportDocument(...)` 基础上新增：

```ts
exportDocumentFile(input: DocumentExportInput): Promise<Blob>
```

或返回更完整对象：

```ts
type DocumentExportFileResponse = {
  blob: Blob;
  filename: string;
  contentType: string;
};
```

前端流程：

1. Word 按钮调用 `exportDocumentFile(...)`；
2. 请求体继续使用 `DocumentExportInput`；
3. `export_format` 使用 `"docx"`；
4. `structured_payload` 传当前 `effectiveScript`；
5. metadata 继续传：
   - `edited`
   - `source_mode`
   - `generated_at`
   - `last_edited_at`
   - `exported_from`
6. 成功后用浏览器下载 blob；
7. 失败时显示产品化错误：
   - “导出失败，请稍后重试或联系技术支持。”

前端不要显示：

- 本机后端地址；
- server path；
- local path；
- API Key；
- `.env` 信息。

## 7. 内容结构

DOCX 第一版建议结构：

1. 标题
   - `project_title`
2. 元信息
   - 来源入口；
   - 使用模型；
   - 生成时间；
   - 编辑时间；
   - 是否编辑稿。
3. 故事梗概
   - `logline`
4. 世界观 / 故事背景
   - `world_setting`
5. 主要人物
   - `name`
   - `role`
   - `age`
   - `personality`
   - `arc`
6. 改编策略
   - adaptation strategy；
   - preserved elements；
   - changed elements；
   - short drama hooks；
   - risk notes。
7. 分集内容
   - 每集标题；
   - 概要；
   - 钩子；
   - 场景；
   - 对白；
   - 画面备注；
   - 情绪备注。

第一版无需复杂页眉、目录、封面、表格模板或批注。

## 8. 安全边界

DOCX 导出必须遵守：

- 不提交生成的 `.docx`；
- 测试只使用安全虚构内容；
- 不写死 `/Users/...`；
- 不返回 `local_path` / `server_path` / `absolute_path`；
- 不记录完整真实剧本文本到日志；
- 不把 API Key 写入 metadata；
- 不把 `.env` 内容写入 metadata；
- 不把服务器路径写入 metadata；
- 文件名必须安全清洗；
- endpoint 不返回本机绝对路径；
- 临时文件如有，必须写入安全临时目录并可清理。

公开仓库只能保留：

- 代码；
- schema；
- 测试；
- 虚构样本；
- 安全文档。

不能提交：

- 真实客户剧本；
- 真实电影剧本；
- 真实小说内容；
- 合作方敏感信息；
- 生成出的真实 Word 文件。

## 9. 测试策略

后端 service 测试：

- `build_docx_export_bytes(...)` 返回 bytes；
- bytes 大于 0；
- 使用 `zipfile` 验证 bytes 是有效 DOCX zip；
- 检查 zip 中存在 `word/document.xml`；
- 检查 `word/document.xml` 包含虚构标题；
- 文件名清洗不包含 `/Users` 或路径分隔符；
- metadata 不包含 API Key / server path / local path。

后端 endpoint 测试：

- `POST /api/documents/export-file` 返回 200；
- `Content-Type` 为 DOCX MIME；
- `Content-Disposition` 包含安全 filename；
- 响应 bytes 是有效 DOCX；
- 缺少 payload 返回清晰错误；
- 非 `docx` 文件导出请求按设计拒绝或转向 JSON endpoint；
- 不返回本机绝对路径。

前端测试：

- `exportDocumentFile(...)` 能处理 blob；
- Word 按钮调用文件导出 API；
- 错误提示产品化；
- e2e 可 route fulfill blob；
- 编辑后 Word 下载 payload 使用 `effectiveScript`。

测试样本必须是虚构内容，不保存真实文件到仓库。

## 10. 分步实施建议

建议后续小步：

1. 第 282 步：引入 `python-docx` 依赖并新增 service bytes 生成
2. 第 283 步：DOCX service 单元测试
3. 第 284 步：新增 `/api/documents/export-file` endpoint
4. 第 285 步：前端 documentExport file API
5. 第 286 步：前端 Word 下载接入
6. 第 287 步：e2e / pytest 覆盖编辑后 Word 导出
7. 第 288 步：更新 README / API_CONTRACT / LOCAL_DEV

每一步都应保持：

- 改动范围小；
- 可单独测试；
- 不提交生成文件；
- 不读取或输出 `.env`；
- 不提交 API Key；
- 不让 `CreationHome` 或 `ShortDramaScriptResult` 膨胀。

## 11. 当前结论

当前结论：

- 不直接把 DOCX 加进现有 JSON endpoint；
- 优先新增文件下载 endpoint；
- `python-docx` 可作为第一版 DOCX 导出依赖；
- 依赖引入必须单独提交、单独测试；
- DOCX 导出是服务器购买前关键能力之一；
- 下一步应先做 service bytes 生成，而不是先改前端按钮。

推荐下一步：

```text
第 282 步：引入 python-docx 依赖并新增 DOCX service bytes 生成
```
