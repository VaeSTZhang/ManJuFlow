# ManJuFlow 真实 LLM 调用测试记录

## 测试目标

本次测试用于验证 ManJuFlow 已经具备从 mock 模式切换到真实 LLM 模式的基础能力。

测试重点不是验证最终剧本质量，而是确认以下链路可以跑通：

- 通过配置切换到 `llm` 模式
- 后端读取 Prompt 文件
- 后端通过 OpenAI-compatible `LLMClient` 调用真实模型
- 模型返回内容可以解析为 JSON
- 解析结果可以通过 `ScriptOutput` 结构校验
- `/api/scripts/generate` 接口仍然作为统一入口返回结构化剧本

## 测试环境

- 本地 Mac 开发环境
- FastAPI 后端
- OpenAI-compatible `LLMClient`
- DeepSeek API
- 接口：`POST /api/scripts/generate`

## 测试输入示例

```text
一个被裁员的中年男人，意外发现公司老板用AI伪造财报
```

## 测试结果

真实 LLM 已成功返回符合 `ScriptOutput` 结构的 JSON。

返回内容包含以下核心字段和子结构：

- `project_title`
- `logline`
- `world_setting`
- `characters`
- `episodes`
- `scenes`
- `dialogues`

本次测试说明：当前后端已经可以从 mock 生成切换到真实 LLM 生成，并完成基础 JSON 解析和 Schema 校验。

## 观察到的问题

- 偶发中文异常空格
- 剧本质量还需要 Prompt 继续优化
- 多集生成稳定性尚未测试
- JSON 解析失败时还需要更完善的错误处理
- 当前尚未保存历史记录

## 中文异常空格问题与修复记录

### 问题现象

真实 LLM 输出中出现过类似异常中文空格：

- `科 技公司`
- `公 司会议室`
- `反 转`
- `二线城 市`
- `还有什 么好怕的？`

### 原因判断

Prompt 约束可以减少这类问题，但无法完全保证模型输出格式稳定。真实模型在生成长文本、中文词组、混合中英文表达时，仍可能产生异常断词或中文标点前后的多余空格。

因此仅依赖 Prompt 不够，需要在代码层增加后处理清洗能力。

### 修复方式

- 新增 `apps/api/app/services/text_cleaner.py`
- 提供 `clean_chinese_spacing`
- 支持递归处理 `dict`、`list`、`str`
- 在真实 LLM 分支中，先完成 JSON 解析，再执行中文空格清洗，最后进行 Pydantic 校验
- 清洗发生在 `ScriptOutput.model_validate(...)` 之前，避免异常空格进入最终结构化结果

### 本地测试样例

以下样例均已通过：

- `二线城 市 => 二线城市`
- `U盘 准备离开 => U盘准备离开`
- `不对 ，这些数字 => 不对，这些数字`
- `大 楼玻璃幕墙 => 大楼玻璃幕墙`
- `还有什 么好怕的？ => 还有什么好怕的？`
- `科 技公司 => 科技公司`
- `公 司会议室 => 公司会议室`
- `反 转 => 反转`

### 当前结论

- Prompt + 后处理清洗组合更稳
- 后续真实 LLM 输出仍需继续观察
- 如果未来有更多异常格式，再扩展清洗规则

## 当前结论

- 真实 LLM 链路已跑通
- 当前默认仍建议保持 `mock` 模式，保证前端演示稳定
- 后续再逐步优化 Prompt、JSON 稳定性和真实生成质量

## Storyboard LLM 测试记录

- 测试日期：2026-04-29
- 测试接口：`POST /api/storyboards/generate`
- 测试模式：`STORYBOARD_GENERATION_MODE=llm`
- 测试结果：HTTP 200 OK
- 测试输入摘要：雨夜医院门口，林晚与顾沉重逢
- 返回结构：`StoryboardOutput`
- 返回内容包含：`scene_id`、`shot_id`、`visual_description`、`ai_image_prompt_hint`
- 生成规模：模型生成 1 个 scene、7 个 shots
- 安全记录：未记录真实 API Key

本次测试说明：第二阶段 Storyboard 真实 LLM 调用链路已跑通，模型返回可通过 `StoryboardOutput` 结构承载，并保留后续“分镜 → AI 绘图 Prompt”所需的稳定字段。

## ImagePrompt DeepSeek LLM 小样本测试记录

- 测试阶段：第三阶段，分镜转 AI 绘图 Prompt
- 测试接口：`POST /api/prompts/generate`
- 测试模式：`IMAGE_PROMPT_GENERATION_MODE=llm`
- 测试目标：验证 `/api/prompts/generate` 在 `IMAGE_PROMPT_GENERATION_MODE=llm` 下可通过 DeepSeek 真实生成 `ImagePromptOutput`

模型配置：

- `LLM_BASE_URL=https://api.deepseek.com`
- `LLM_MODEL=deepseek-chat`
- `LLM_API_KEY` 已配置，但不记录真实 key
- `IMAGE_PROMPT_GENERATION_MODE=llm`

测试输入摘要：

- 项目标题：测试短剧：雨夜重逢
- 场景：医院门口雨夜重逢
- 镜头：林晚撑黑伞站在医院门口；顾沉从黑色轿车下来，两人在车灯和雨幕中对视

返回结果摘要：

- 返回合法 `ImagePromptOutput`
- 包含 2 条 `ImagePromptItem`
- `prompt_id` 包含 `P001` / `P002`
- `shot_id` 包含 `S001_SH001` / `S001_SH002`
- `positive_prompt` 为英文绘图 Prompt
- `negative_prompt` 包含 `low quality`、`blurry`、`bad anatomy`、`watermark`、`text`、`logo` 等负面词

结论：

- DeepSeek `llm` 模式小样本通过
- `parse_image_prompt_llm_response` 能成功解析真实模型输出
- `ImagePromptOutput` 数据协议可支撑真实 LLM 输出

注意事项：

- `python -m json.tool` 会将中文显示为 Unicode 转义，这是正常现象
- 测试后应切回 `IMAGE_PROMPT_GENERATION_MODE=mock`，避免日常开发消耗 token
- 后续仍需更多题材、更多镜头数量、多角色一致性测试

## 下一步建议

- 优化 `idea_to_script_v1.md`
- 增加 JSON 清洗 / 修复逻辑
- 增加错误提示
- 增加历史记录
- 再扩展到“剧本 → 分镜”
