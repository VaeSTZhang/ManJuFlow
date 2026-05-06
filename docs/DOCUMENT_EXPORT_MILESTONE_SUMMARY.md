# Document Export Milestone Summary｜文档导出闭环阶段总结

## 1. 当前已完成能力

Dramora 已完成短剧剧本 Document Export 第一版闭环，当前能力包括：

- 后端 `DocumentExportInput` / `DocumentExportOutput` schema；
- TXT 导出 service；
- JSON 导出 service；
- `POST /api/documents/export` TXT / JSON JSON endpoint；
- DOCX bytes service；
- `POST /api/documents/export-file` DOCX 文件下载 endpoint；
- 前端 `documentExport` client；
- 前端 JSON / TXT 下载走后端 `/api/documents/export`；
- 前端 Word 下载走后端 `/api/documents/export-file`；
- 前端导出使用当前有效稿 `effectiveScript`；
- e2e 覆盖编辑后 TXT / JSON / Word 导出数据流。

当前导出链路已经从“浏览器本地临时下载”升级为“前端提交当前有效稿 → 后端导出契约 → 前端下载文件”。

## 2. 后端接口清单

### `POST /api/documents/export`

用途：

- 导出文本类内容；
- 当前支持 `txt` / `json`；
- 返回 JSON `DocumentExportOutput`。

返回特点：

- `content_text` 承载导出内容；
- `filename` 由后端清洗或生成；
- `file_size_bytes` 按 UTF-8 字节数计算；
- `metadata` 保留安全追踪字段；
- 不写文件；
- 不返回本机路径。

### `POST /api/documents/export-file`

用途：

- 导出文件类内容；
- 当前支持 `docx`；
- 返回 DOCX bytes。

返回特点：

- `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`；
- `Content-Disposition: attachment; filename="..."`；
- 使用安全文件名；
- 使用 `BytesIO` 生成 bytes；
- 不长期落盘；
- 不返回 `server_path` / `local_path` / `absolute_path`。

## 3. 安全边界

Document Export 当前必须继续遵守：

- 不落真实客户文件；
- 不提交生成的 `.docx`；
- 不提交真实客户剧本；
- 不提交真实电影剧本；
- 不提交真实小说内容；
- 不返回 `server_path` / `local_path` / `absolute_path`；
- 不写死 `/Users/...`；
- 测试只使用安全虚构内容；
- API Key 不进入导出 payload；
- `.env` 不进入导出 metadata；
- 服务器路径不进入导出 metadata；
- 日志不记录完整真实剧本内容。

公开仓库只能保留代码、schema、测试、虚构样本和安全文档。

## 4. 自动化测试清单

后端测试：

- `tests/api/test_document_schema.py`
- `tests/api/test_document_export_service.py`
- `tests/api/test_document_export_endpoint.py`
- `tests/api/test_document_docx_export_service.py`
- `tests/api/test_document_export_file_endpoint.py`

前端 e2e：

- `apps/web/tests/e2e/creation-home.spec.ts`

当前 e2e 覆盖：

- 编辑后 TXT 下载使用编辑稿；
- 编辑后 JSON 复制使用编辑稿；
- 编辑后角色字段进入导出 payload；
- 编辑后分集字段进入导出 payload；
- 编辑后 Word 下载请求 `/api/documents/export-file`；
- Word 下载 payload 使用编辑后的 `effectiveScript`；
- Word 下载 metadata 标记 `edited=true` 和 `exported_from="creation_home"`。

## 5. 当前未做

当前导出闭环第一版明确未做：

- DOCX 高级模板；
- DOCX 封面；
- DOCX 批注；
- DOCX 修订痕迹；
- PDF 导出；
- 云端文件保存；
- 文件历史版本；
- 批量导出；
- scenes / dialogues 深层在线编辑；
- 真实存储服务；
- 多人协作；
- 复杂权限审计；
- 对象存储；
- 服务器部署。

这些能力不应继续挤进当前 Document Export 第一版，后续必须分别设计和验收。

## 6. 下一阶段建议

Document Export 第一版闭环完成后，下一阶段建议优先进入：

- 真实模型质量验收；
- 内部账号 / 权限基础；
- UsageLedger / 用量记录；
- 结构与 README 更新；
- 部署前安全扫描；
- 前后端配置与环境检查；
- 私有部署前运行手册。

当前不建议继续深挖复杂 DOCX 排版。原因：

- 老板和内部用户第一阶段更关心能否生成、编辑、下载；
- 当前 Word 已能承载交付内容；
- 继续做复杂模板会延后真实试用；
- 模型质量、账号、用量、安全和部署治理更接近内部试用前置条件。

## 7. 回归命令

后续每次修改 Document Export 相关代码，至少运行：

```bash
python -m pytest tests/api/test_document_schema.py tests/api/test_document_export_service.py tests/api/test_document_export_endpoint.py tests/api/test_document_docx_export_service.py tests/api/test_document_export_file_endpoint.py
```

如果本机 `python` 不可用，应使用项目虚拟环境：

```bash
/path/to/Dramora/.venv/bin/python -m pytest tests/api/test_document_schema.py tests/api/test_document_export_service.py tests/api/test_document_export_endpoint.py tests/api/test_document_docx_export_service.py tests/api/test_document_export_file_endpoint.py
```

前端回归：

```bash
cd apps/web
npm run build
npm run test:e2e
```

说明：

- e2e 应继续使用 route fulfill，不真实调用外部模型；
- 测试样本必须保持虚构；
- 不提交下载产生的文件。

## 8. 当前结论

Document Export 第一版已达到内部试用前置要求。

当前完成度：

- 生成结果可在线编辑；
- 编辑稿可复制 JSON；
- 编辑稿可下载 TXT；
- 编辑稿可下载 Word；
- 后端导出契约已建立；
- 前端已接入后端导出；
- pytest 和 e2e 已覆盖关键数据流。

后续不应继续深挖复杂排版，而应进入真实模型质量、账号用量和部署前治理。
