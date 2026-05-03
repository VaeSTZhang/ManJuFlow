# Phase 5 Long Script Input Limit and Chunking Design｜长剧本文本限制与分块策略设计

## 1. 设计目标

本文档用于在实现真实上传接口和后续 LLM 切分前，先明确第五阶段已有剧本输入的长度边界和分块处理策略。

本设计需要回答：

- 粘贴已有剧本文本的最大长度；
- 上传 `.docx` 后 `extracted_text` 的最大长度；
- 长剧本如何进入 `Script Segmentation`；
- 为什么不能把 10 万字直接一次性发送给 LLM；
- 如何通过 chunking 保证质量、可回溯、可重试、可统计成本。

本步骤只做设计，不修改后端代码、不修改前端代码、不新增依赖、不接真实 LLM。

## 2. 产品层限制建议

第五阶段已有剧本输入支持两种方式。

方式 A：粘贴文本

- 建议最大 100,000 字符；
- 前端显示当前字符数；
- 超过限制时禁止提交，或提示用户拆分后再提交。

方式 B：上传 `.docx`

- 第一版建议文件大小限制为 10 MB；
- 提取后的 `extracted_text` 最大 100,000 字符；
- 暂不优先支持 `.doc`；
- `.doc` 文件提示用户另存为 `.docx` 后再上传。

这里的 100,000 是系统接收和管理的文本字符上限，不是单次 LLM 调用上限。

## 3. 为什么 10 万字不能一次性丢给大模型

即使系统允许用户粘贴或上传约 100,000 字符，也不应把全部内容一次性发送给 LLM。

主要风险包括：

- 模型上下文可能不足；
- 即使上下文足够，也容易忽略中间内容；
- 输出 JSON 过长，解析失败概率高；
- 失败后重试成本高；
- 速度慢；
- token 成本高；
- 难以定位是哪一段失败；
- 不利于 `UsageLedger` 成本拆分；
- 不利于项目级审计和回溯。

结论：系统可以接收 100,000 字符级别的剧本，但 AI 处理必须分块。

## 4. 分块策略建议

建议后续在 `Script Segmentation` 处理长文本时预留以下参数：

- `max_input_chars`: 100000
- `chunk_size_chars`: 6000 到 10000
- `chunk_overlap_chars`: 300 到 500
- `chunking_strategy`: `paragraph_first`
- `preserve_paragraph_order`: `true`

推荐策略：

- 优先按段落切分；
- 段落过长时再按字符切分；
- 保留段落顺序；
- 保留 episode / scene / dialogue 等剧本标记；
- 每个 chunk 生成稳定 `chunk_id`；
- chunk 之间保留少量 overlap，避免语义断裂；
- 日志中不打印完整 chunk 内容。

## 5. Script Segmentation 分块处理流程

建议未来流程：

```text
用户粘贴或上传剧本
  -> extracted_text
  -> validate length
  -> normalize text
  -> create ScriptTextChunk[]
  -> 对每个 chunk 做 segmentation
  -> 合并 ScriptSegment
  -> 修正 segment_id / episode_number / scene_number
  -> 返回 ScriptSegmentationOutput
```

mock 阶段可以先不真正切块，但 Schema、metadata、测试和文档应预留分块能力，避免未来真实 LLM 接入时返工。

## 6. 建议新增的未来数据结构

后续可以单独新增 Schema，不在本步骤写代码。

`ScriptTextChunk` 可包含：

- `chunk_id`
- `source_id`
- `chunk_index`
- `start_char`
- `end_char`
- `text`
- `char_count`
- `overlap_with_previous`
- `metadata`

`ChunkSegmentationResult` 可包含：

- `chunk_id`
- `segments`
- `status`
- `error_message`
- `token_usage`
- `estimated_cost_cny`
- `metadata`

这些结构的目标是让长剧本处理可追踪、可重试、可计费、可审计。

## 7. 与 Upload Source 的关系

`UploadSourceMetadata` 后续可以直接字段化，或先通过 `metadata` 记录：

- `extracted_text_length`
- `max_input_chars`
- `chunk_count`
- `chunking_strategy`
- `truncated`
- `validation_status`

`ScriptUploadOutput` 返回 `extracted_text` 时：

- MVP 可以返回完整 `extracted_text`；
- 如果超过前端展示压力，后续可以只返回 preview + `source_id`；
- 前端再通过 `source_id` 拉取全文或分页查看。

前端不应依赖后端本地文件路径，后续仍应通过 `source_id`、`extracted_text` 和 metadata 进入 `Script Segmentation`。

## 8. 与 UsageLedger 的关系

长剧本切分可能触发多次 LLM 调用，因此 `UsageLedger` 需要支持父请求和 chunk 级记录。

单个 chunk 调用建议记录：

- `parent_request_id`
- `chunk_id`
- `chunk_index`
- `feature_name=script_segmentation`
- `operation_type=segment_script_chunk`
- token usage
- `estimated_cost_cny`
- `status`

最终汇总建议记录：

- `total_chunks`
- `succeeded_chunks`
- `failed_chunks`
- `total_estimated_cost_cny`

这样可以按项目、用户、workspace、chunk 和失败原因回溯成本与质量。

## 9. 前端提示建议

前端应在粘贴和上传区域显示清晰限制：

- 当前字符数；
- 最大字符数；
- 上传文件大小限制；
- 支持格式 `.docx`；
- `.doc` 暂不支持；
- 长剧本会自动分段处理；
- 生成时间可能更长；
- 生产环境必须登录后才能上传和切分。

建议提示文案：

```text
当前支持最多约 100,000 字符。系统会在后端自动分段处理，避免超长剧本导致 AI 解析不稳定。
```

## 10. 错误处理建议

建议错误类型：

- `SCRIPT_TEXT_TOO_LONG`
- `UPLOAD_FILE_TOO_LARGE`
- `UNSUPPORTED_FILE_TYPE`
- `EXTRACTED_TEXT_EMPTY`
- `EXTRACTED_TEXT_TOO_LONG`
- `CHUNKING_FAILED`
- `PARTIAL_SEGMENTATION_FAILED`

错误信息应给用户明确可操作建议：

- 缩短文本；
- 拆分剧本；
- 转换为 `.docx`；
- 删除无关页眉页脚；
- 稍后重试。

后端日志不应打印完整剧本、完整 chunk、客户素材或敏感上下文。

## 11. 验收标准

第 150.1 步验收标准：

- `docs/PHASE_5_LONG_SCRIPT_INPUT_LIMIT_AND_CHUNKING_DESIGN.md` 已新增；
- 文档明确粘贴文本最大 100,000 字符；
- 文档明确 `.docx` 文件大小第一版建议 10 MB；
- 文档明确 `extracted_text` 最大 100,000 字符；
- 文档明确 10 万字符不是单次 LLM 调用上限；
- 文档明确 chunking 策略；
- 文档明确与 Upload Source、Script Segmentation、UsageLedger、前端提示的关系；
- 不修改代码；
- 不新增依赖；
- 不引入真实剧本或敏感信息。
