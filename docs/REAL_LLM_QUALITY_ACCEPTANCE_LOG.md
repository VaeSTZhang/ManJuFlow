# Real LLM Quality Acceptance Log｜真实模型质量验收日志

## 1. 文档目的

本日志用于记录 Dramora 真实 LLM 小样本验收摘要，帮助团队在老板实操和内部试用前确认三入口生成 / 改编链路的可用性、稳定性、内容质量和错误处理情况。

本文件只记录验收摘要，不记录：

- API Key；
- `.env` 内容；
- 本机绝对路径；
- 真实客户剧本；
- 真实电影剧本；
- 真实小说原文；
- 合作方敏感内容；
- 完整真实模型输出。

## 2. 记录规则

- 只使用安全虚构样本；
- 只记录输入摘要，不粘贴长文本；
- 只记录输出结构摘要，不粘贴完整输出；
- 不记录 API Key；
- 不记录 `.env`；
- 不记录本机绝对路径；
- 不记录真实客户 / 合作方内容；
- 不提交真实剧本；
- 不提交完整真实模型输出；
- 失败记录只保留现象、可能原因、严重程度和下一步处理建议。

## 3. 验收表格模板

| Date | Provider | Model | Source Mode | Sample ID | Generation Mode | Schema Result | Quality Result | Product Flow Result | Issues | Next Action | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | provider | model | idea / film_script / novel | sample_id | llm | pending | pending | pending | pending | pending | Do not paste full model output. |

字段说明：

- Date：验收日期；
- Provider：模型 provider，例如 deepseek / mimo / kimi / minimax；
- Model：具体模型名称；
- Source Mode：入口类型；
- Sample ID：安全虚构样本编号；
- Generation Mode：应为 llm；
- Schema Result：结构验收结果；
- Quality Result：质量评价结果；
- Product Flow Result：是否可进入前端展示、在线编辑和导出；
- Issues：问题摘要；
- Next Action：下一步动作；
- Notes：补充说明，不记录敏感内容。

## 4. 质量评价标准

可复用枚举：

- `pass`：可进入内部试用；
- `usable_with_minor_issues`：可用，但需要 prompt 或文案优化；
- `needs_prompt_fix`：结构可用，但内容质量明显不足；
- `schema_failed`：结构不符合 `ShortDramaScriptOutput`；
- `provider_failed`：provider 调用失败；
- `blocked`：配置、安全或环境原因阻塞。

建议使用方式：

- Schema Result：优先使用 `pass` / `schema_failed` / `provider_failed` / `blocked`；
- Quality Result：优先使用 `pass` / `usable_with_minor_issues` / `needs_prompt_fix`；
- Product Flow Result：优先记录是否能进入结果展示、在线编辑、TXT / JSON / Word 导出。

## 5. 三入口样本 ID

预留安全样本 ID：

- `idea_safe_sample_001`；
- `film_script_safe_sample_001`；
- `novel_safe_sample_001`。

样本正文见 `docs/REAL_LLM_QUALITY_ACCEPTANCE_PLAN.md`。本日志只记录样本 ID 和摘要，不重复粘贴长文本。

## 6. DeepSeek 验收区

DeepSeek 是当前内部默认推荐模型，三入口应完整验收。

| Date | Provider | Model | Source Mode | Sample ID | Generation Mode | Schema Result | Quality Result | Product Flow Result | Issues | Next Action | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | deepseek | deepseek-chat | idea | idea_safe_sample_001 | llm | pending | pending | pending | pending | Run safe sample acceptance. | Template only. |
| TBD | deepseek | deepseek-chat | film_script | film_script_safe_sample_001 | llm | pending | pending | pending | pending | Run safe sample acceptance. | Template only. |
| TBD | deepseek | deepseek-chat | novel | novel_safe_sample_001 | llm | pending | pending | pending | pending | Run safe sample acceptance. | Template only. |

## 7. Mimo / Kimi / MiniMax 抽检区

Mimo / Kimi / MiniMax 已保留 provider 扩展能力。真实 API 抽检不需要每次全量运行，按成本、稳定性和内部试用需要执行。

| Date | Provider | Model | Source Mode | Sample ID | Generation Mode | Schema Result | Quality Result | Product Flow Result | Issues | Next Action | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | mimo | TBD | idea / film_script / novel | TBD | llm | pending | pending | pending | pending | Optional sample acceptance. | Template only. |
| TBD | kimi | TBD | idea / film_script / novel | TBD | llm | pending | pending | pending | pending | Optional sample acceptance. | Template only. |
| TBD | minimax | TBD | idea / film_script / novel | TBD | llm | pending | pending | pending | pending | Optional sample acceptance. | Template only. |

## 8. 问题记录模板

| Issue ID | Provider | Source Mode | Symptom | Possible Cause | Severity | Proposed Fix | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LLM-QA-001 | provider | idea / film_script / novel | Short symptom only. | Do not include secrets or full output. | low / medium / high / blocker | Prompt / parser / config / UI fix. | open / fixed / deferred |

记录要求：

- Symptom 只写现象摘要；
- Possible Cause 不粘贴完整 provider 响应；
- Proposed Fix 应明确是 prompt 优化、parser 容错、配置修复还是前端提示优化；
- Status 应及时更新；
- 不记录完整真实模型输出。

## 9. 当前状态

当前仅建立日志模板，尚未执行新的真实 API 质量验收。

下一步建议：

- 第 289 步：DeepSeek 三入口小样本验收；
- 第 290 步：根据 DeepSeek 输出优化 prompt；
- 第 291 步：Mimo / Kimi / MiniMax 抽检计划或可选验收；
- 第 292 步：更新 README / LLM_SETUP 中真实模型验收状态。
