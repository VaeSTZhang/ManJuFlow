# ManJuFlow 四模型 ImagePrompt 输出质量对比记录

## 1. 记录目的

- 本文档用于记录 DeepSeek / Mimo / Kimi / MiniMax 在标准 ImagePrompt 样本上的输出质量；
- 输入样本来自 `tests/fixtures/image_prompt_samples/`；
- 评分标准来自 `docs/MODEL_COMPARISON_PLAN.md`；
- 本文档不保存 API Key；
- 暂不做自动评分，先人工记录。

## 2. 测试前置条件

- 确保 `.env` 中四家 provider key 已配置；
- 默认保持 `IMAGE_PROMPT_GENERATION_MODE=mock`；
- 每次测试只切换一个 provider；
- 修改 `.env` 后重启后端；
- 每次测试后切回 mock；
- 所有 provider 使用同一份样本 JSON；
- 保存输出时不要记录真实 API Key。
- 运行前参考 `docs/MODEL_COMPARISON_RUNBOOK.md`。

## 3. Provider 配置记录

| provider | model | base_url | special_notes |
| --- | --- | --- | --- |
| deepseek | deepseek-chat | `https://api.deepseek.com` | 常规 `temperature=0.7` |
| mimo | mimo-v2.5-pro | `https://api.xiaomimimo.com` | 使用 sk key，tp key 不用于后端直连 |
| kimi | kimi-k2.5 | `https://api.moonshot.cn` | k2.x 需要 `temperature=1.0`，实际返回可能 `kimi-k2.6` |
| minimax | MiniMax-M2.7 | `https://api.minimaxi.com` | 中国区 endpoint，`api.minimax.io` 对当前 key 返回 401 |

## 4. 样本清单

| sample_id | sample_type | fixture_path | core_test_points |
| --- | --- | --- | --- |
| S001 | 都市情感雨夜重逢 | `tests/fixtures/image_prompt_samples/S001_urban_rain_reunion.json` | 雨夜、冷色光影、双人对峙 |
| S002 | 悬疑反转办公室 | `tests/fixtures/image_prompt_samples/S002_suspense_office_reversal.json` | 文件道具、玻璃反射、悬疑钩子 |
| S003 | 年代旧宅对峙 | `tests/fixtures/image_prompt_samples/S003_period_courtyard_confrontation.json` | 年代感、服化道、雨夜旧宅 |
| S004 | 多角色家庭冲突 | `tests/fixtures/image_prompt_samples/S004_multi_character_family_conflict.json` | 五人空间关系、饭桌构图、情绪爆发 |

## 5. 总评分表

| sample_id | provider | model | json_valid | item_count | visual_score | fidelity_score | consistency_score | camera_score | negative_prompt_score | language_score | latency_seconds | cost_note | overall_score | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S001 | deepseek | deepseek-chat | yes | 2 | 4 | 4 | 4 | 4 | 4 | 4 |  |  | 4 | 英文 prompt 清晰稳定，雨夜、车灯、湿地反光表达完整；结构合法。 |
| S001 | mimo | mimo-v2.5-pro | yes | 2 | 4 | 4 | 4 | 4 | 4 | 4 |  |  | 4 | 英文 prompt 稳定，氛围和角色一致性较好，细节完整；结构合法。 |
| S001 | kimi | kimi-k2.5 | yes | 2 | 4 | 4 | 4 | 4 | 4 | 3 |  |  | 4 | 输出结构合法，画面感较强；中文字段出现少量异常空格，后续可考虑 ImagePrompt parser 后处理清洗。 |
| S001 | minimax | MiniMax-M2.7 | yes | 2 | 4 | 4 | 4 | 4 | 4 | 3 |  |  | 4 | 输出结构合法，画面感较强；中文字段出现少量异常空格，后续可考虑 ImagePrompt parser 后处理清洗。 |
| S002 | deepseek | deepseek-chat |  |  |  |  |  |  |  |  |  |  |  |  |
| S002 | mimo | mimo-v2.5-pro |  |  |  |  |  |  |  |  |  |  |  |  |
| S002 | kimi | kimi-k2.5 |  |  |  |  |  |  |  |  |  |  |  |  |
| S002 | minimax | MiniMax-M2.7 |  |  |  |  |  |  |  |  |  |  |  |  |
| S003 | deepseek | deepseek-chat |  |  |  |  |  |  |  |  |  |  |  |  |
| S003 | mimo | mimo-v2.5-pro |  |  |  |  |  |  |  |  |  |  |  |  |
| S003 | kimi | kimi-k2.5 |  |  |  |  |  |  |  |  |  |  |  |  |
| S003 | minimax | MiniMax-M2.7 |  |  |  |  |  |  |  |  |  |  |  |  |
| S004 | deepseek | deepseek-chat |  |  |  |  |  |  |  |  |  |  |  |  |
| S004 | mimo | mimo-v2.5-pro |  |  |  |  |  |  |  |  |  |  |  |  |
| S004 | kimi | kimi-k2.5 |  |  |  |  |  |  |  |  |  |  |  |  |
| S004 | minimax | MiniMax-M2.7 |  |  |  |  |  |  |  |  |  |  |  |  |

## 6. 异常记录表

| date | sample_id | provider | model | error_type | error_message | resolution | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

## 7. 初步结论区

待完成第一轮四模型标准样本测试后填写。

当前不得根据单个样本过度下结论。结论应同时考虑质量、稳定性、成本、速度和后续生产链路适配。

## 8. 后续动作

1. 逐个 provider 跑 S001-S004；
2. 保存输出 JSON；
3. 按评分维度人工打分；
4. 汇总最佳默认 provider；
5. 决定是否进入前端模型选择器设计；
6. 若发现某 provider 输出异常，优先优化 Prompt 或 parser，再考虑 provider 特化。

运行前参考 `docs/MODEL_COMPARISON_RUNBOOK.md`。


## 9. S001 第一轮观察

S001 都市情感雨夜重逢样本已完成 DeepSeek / Mimo / Kimi / MiniMax 四模型第一轮测试。

初步观察：

- 四家 provider 均返回合法 `ImagePromptOutput`；
- 四家 provider 均返回 2 条 `ImagePromptItem`；
- DeepSeek 和 Mimo 的英文 prompt 稳定，中文字段较少；
- Kimi 和 MiniMax 的画面感较强，但中文字段出现少量异常空格；
- 当前不根据单个样本确定最终默认模型；
- 后续需要继续跑 S002-S004，再综合判断稳定性、画面感、忠实度、成本和速度。
