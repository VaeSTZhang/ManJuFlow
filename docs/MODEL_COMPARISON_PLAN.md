# ManJuFlow 四模型 ImagePrompt 输出质量对比方案

## 1. 目标

- 当前四家 provider 已完成 ImagePrompt 小样本验收。
- 下一步不是继续盲目扩展模型，而是建立质量评估标准。
- 目标是比较 DeepSeek / Mimo / Kimi / MiniMax 在“分镜转 AI 绘图 Prompt”任务上的实际可用性。
- 对比结果将影响后续默认模型选择、前端模型选择器、成本控制和生产链路策略。

## 2. 对比模型范围

- `deepseek`：`deepseek-chat`
- `mimo`：`mimo-v2.5-pro`
- `kimi`：`kimi-k2.5`，实际返回可能显示 `kimi-k2.6`
- `minimax`：`MiniMax-M2.7`

说明：

- 当前不接入 Qwen。
- 后续可按公司实际需求增删 provider。
- TTS / 多模态模型不纳入本次 ImagePrompt 文本对比。

## 3. 统一测试输入

建议至少准备 4 类样本：

1. 都市情感雨夜重逢

   - 用当前“雨夜医院门口”样本作为基线；
   - 重点看雨夜氛围、角色对峙、冷色光影。

2. 悬疑反转办公室

   - 例如主角在公司会议室发现隐藏证据；
   - 重点看悬疑氛围、道具细节、镜头钩子。

3. 古风/民国/年代场景

   - 例如雨中庭院、码头离别、旧宅对峙；
   - 重点看时代感、服化道、场景准确性。

4. 多角色复杂场面

   - 例如 3-5 人冲突、宴会、审判、家庭对峙；
   - 重点看角色一致性、空间关系、避免人物混乱。

说明：

- 所有模型必须使用同一份 `ImagePromptInput`。
- 每个模型至少跑相同样本。
- 不做大批量消耗，先小样本稳定评估。

## 4. 评分维度

建议使用 1-5 分评分。

1. JSON 稳定性

   - 是否返回合法 JSON；
   - 是否能通过 `ImagePromptOutput` 校验；
   - 是否出现 markdown fence / 多余解释 / 缺字段。

2. 视觉画面感

   - `positive_prompt` 是否有清晰画面；
   - 是否能直接给绘图模型使用；
   - 是否有镜头感、光影、构图、环境细节。

3. 分镜忠实度

   - 是否忠实保留原 storyboard 的场景、人物、动作；
   - 是否擅自添加新角色、新地点、新剧情。

4. 角色一致性

   - 是否能维护人物外观、服装、动作连续性；
   - 多镜头之间是否保持同一角色描述一致。

5. 镜头语言质量

   - `camera_language` 是否具体；
   - 是否有景别、机位、运动、构图逻辑。

6. 负面词完整度

   - `negative_prompt` 是否覆盖 `low quality`、`blurry`、`bad anatomy`、`extra fingers`、`watermark`、`text`、`logo` 等；
   - 是否能根据场景补充无关风格排除项。

7. 中文理解与跨语言表达

   - 是否理解中文分镜；
   - 是否能输出适合绘图模型的英文 `positive_prompt`；
   - 中文字段是否自然准确。

8. 成本与速度

   - 记录响应时间；
   - 记录 token / credit 消耗；
   - 不作为唯一标准，但作为生产选型参考。

## 5. 推荐记录表

| sample_id | sample_type | provider | model | json_valid | item_count | visual_score | fidelity_score | consistency_score | camera_score | negative_prompt_score | language_score | latency_seconds | cost_note | overall_score | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S001 | 都市情感雨夜重逢 | deepseek | deepseek-chat | yes | 2 |  |  |  |  |  |  |  |  |  |  |

## 6. 对比流程

建议流程：

1. 确保 `.env` 中四家 provider key 都已配置；
2. 默认保持 `IMAGE_PROMPT_GENERATION_MODE=mock`；
3. 每次只切换一个 provider；
4. 修改 `.env` 后重启后端；
5. 使用相同 curl 输入测试 `/api/prompts/generate`；
6. 保存每次模型输出；
7. 按评分维度人工打分；
8. 记录异常，包括 401、400、parser 失败、JSON 不稳定等；
9. 测试后切回 mock；
10. 将结论写入 `LLM_TEST_LOG` 或后续专门的模型对比记录文档。

## 7. 初步观察

根据目前小样本测试，先记录初步观察，不做过度结论：

- DeepSeek 已稳定通过 ImagePrompt 小样本；
- Mimo 已稳定通过 ImagePrompt 小样本；
- Kimi 可用，但 k2.x 对 temperature 有限制，`LLMClient` 已适配 `temperature=1.0`；
- MiniMax 可用，但 endpoint 需要注意区域，中国区使用 `https://api.minimaxi.com`；
- 四家都能输出合法 `ImagePromptOutput`；
- 仍需更多题材和更多镜头数量验证。

## 8. 暂不做

- 不做自动打分系统；
- 不做大批量压测；
- 不接文生图；
- 不接 ComfyUI；
- 不做前端模型选择器实现；
- 不接阿里 Qwen；
- 不做多 Agent 调度。

## 9. 下一步建议

- 准备 4 个标准测试样本；
- 为每个样本生成统一 `ImagePromptInput` JSON；
- 逐个 provider 跑小样本；
- 形成 DeepSeek / Mimo / Kimi / MiniMax 对比表；
- 再决定前端模型选择器和默认模型策略。
