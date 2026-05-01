# ManJuFlow 四模型 ImagePrompt 标准测试样本

## 1. 目的

这些样本用于 DeepSeek / Mimo / Kimi / MiniMax 的 ImagePrompt 输出质量对比。每个样本都是固定的 ImagePromptInput JSON，用来保证不同 provider 在相同输入下评估。

## 2. 样本列表

| sample_id | 文件路径 | 样本类型 | 核心测试点 |
| --- | --- | --- | --- |
| S001 | `tests/fixtures/image_prompt_samples/S001_urban_rain_reunion.json` | 都市情感雨夜重逢 | 雨夜、冷色光影、双人对峙 |
| S002 | `tests/fixtures/image_prompt_samples/S002_suspense_office_reversal.json` | 悬疑反转办公室 | 文件道具、玻璃反射、悬疑钩子 |
| S003 | `tests/fixtures/image_prompt_samples/S003_period_courtyard_confrontation.json` | 年代旧宅对峙 | 年代感、服化道、雨夜旧宅 |
| S004 | `tests/fixtures/image_prompt_samples/S004_multi_character_family_conflict.json` | 多角色家庭冲突 | 五人空间关系、饭桌构图、情绪爆发 |

## 3. 使用方式

- 每个样本都是 ImagePromptInput JSON；
- 后续四模型对比时，每个 provider 都使用同一份样本；
- 每次只切换一个 provider；
- 修改 `.env` 后需要重启后端；
- 测试后切回 `IMAGE_PROMPT_GENERATION_MODE=mock`；
- 输出结果可记录到后续模型对比表。

## 4. 暂不做

- 本步不调用真实 LLM；
- 不做自动评分；
- 不接文生图；
- 不做前端模型选择器；
- 不做批量压测。
