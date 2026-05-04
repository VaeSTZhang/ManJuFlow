# Script Creation LLM Milestone｜剧本创作真实模型闭环里程碑

## 1. 里程碑结论

Dramora 当前已完成“三入口真实 AI 剧本生成与改编闭环”。

已完成能力：

- 灵感生成短剧剧本；
- 电影剧本改编短剧本；
- 小说 / 网文改编短剧本；
- 三入口均支持 DeepSeek 真实 LLM 小样本；
- 前端三入口真实 LLM 浏览器验收通过；
- 输出统一 `ShortDramaScriptOutput`；
- 前端统一结果页展示；
- JSON / TXT 导出可用；
- Word 导出仍是后续闭环。

这意味着 Dramora 的第一主线“剧本创作生成 / 剧本改编”已经具备可演示、可验收、可继续产品化的真实模型链路。

## 2. 当前能力清单

### 前端

- `CreationHome`：承载灵感生成、电影剧本改编、小说 / 网文改编三入口；
- `CreativeModelPanel`：统一创作模型选择，支持 DeepSeek / Mimo / Kimi / MiniMax / 后端默认；
- `ShortDramaScriptResult`：统一展示 `ShortDramaScriptOutput`；
- Word 导入预览确认：导入后由用户选择填入、追加或取消，避免覆盖正在编辑的文本；
- JSON / TXT 下载：结果生成后可复制或导出结构化内容。

### 后端

- `POST /api/scripts/generate-from-source`：三入口统一剧本生成 API；
- `AIRequestOptions`：请求级模型选择与用途声明；
- `generate_short_drama_script` mode gateway：统一分发 `mock` / `llm` 模式；
- idea / film_script / novel LLM path：三入口均已具备真实 LLM 调用路径；
- metadata provider/model/purpose 追踪：返回结果可追踪生成模式、provider、model、purpose；
- provider-aware `llm_enabled`：`/api/system/status` 会根据默认 provider 对应 key 判断 LLM 可用状态。

### 测试

- pytest 全量 API 测试通过；
- 前端 `npm run build` 通过；
- DeepSeek smoke tests 已覆盖 idea / film_script / novel；
- browser acceptance 已覆盖前端三入口真实 LLM 生成、结果展示、JSON / TXT 导出。

## 3. 当前默认模型与扩展原则

- DeepSeek 是内部默认推荐模型；
- DeepSeek 不应写死在业务逻辑中；
- Mimo / Kimi / MiniMax 可通过 `CreativeModelPanel` 和 `AIRequestOptions` 扩展；
- 后续不要在业务 service 中散写 provider 判断；
- provider / model 选择应优先通过统一配置、`AIRequestOptions` 或 `LLMClient` provider adapter 管理。

当用户在前端选择“后端默认”时，后端应使用 `DEFAULT_LLM_PROVIDER` / `DEFAULT_SCRIPT_MODEL` 等统一配置入口。

## 4. 安全边界

- `.env` 只在本地；
- `.env` 不提交；
- 测试样本均为虚构；
- 不使用真实客户剧本；
- 不打印 API Key；
- 公开仓库仅保留模板、代码、mock、安全示例和文档；
- 真实模型调用记录只记录 provider / model / purpose / generation_mode 等轻量追踪字段，不记录完整客户输入或密钥。

## 5. 当前仍未完成

- 真实 Word `.docx` 上传解析；
- 真实 Word `.docx` 导出；
- 结果在线编辑和人工修订版；
- 内部真实账号 / 登录；
- `UsageLedger`；
- 质量评审；
- 剧本 -> 分镜 -> Prompt 第二大功能重接入；
- 服务器部署不在当前阶段。

当前版本不规划右侧聊天式 AI Assistant / AssistantPanel / `/api/assistant/chat` / `suggested_actions`，历史方案仅归档。这不代表取消核心 LLM 创作能力；三入口剧本生成与改编、扩写、质量评审和后续分镜 / Prompt 生成仍继续通过 DeepSeek / Mimo / Kimi / MiniMax 等模型推进。

## 6. 下一步建议

- 第 235 步：真实 Word 导入契约设计；
- 第 236 步：`python-multipart` / `python-docx` 依赖与后端上传接口；
- 第 237 步：前端 Word 上传接真实接口；
- 第 238 步：Document Export service；
- 第 239 步：前端下载 Word 接真实导出；
- 第 240 步：结果在线编辑第一版。
