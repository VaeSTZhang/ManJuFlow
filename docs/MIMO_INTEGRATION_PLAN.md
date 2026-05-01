# ManJuFlow Mimo / 小米大模型接入方案

## 1. 接入目标

- 将 Mimo / 小米大模型作为 ManJuFlow 的可选 LLM 模型接入。
- 不替代现有 DeepSeek，而是作为 OpenAI-compatible 模型选项。
- 优先服务于第三阶段 ImagePrompt 生成测试。
- 后续可扩展到剧本生成、分镜生成、TTS 配音等环节。

## 2. 当前项目已有基础

- 已有 OpenAI-compatible `LLMClient`。
- 已有 `LLM_BASE_URL` / `LLM_MODEL` / `LLM_API_KEY` 配置。
- DeepSeek 已完成 script / storyboard / image prompt 小样本真实调用。
- ImagePrompt 已支持 `IMAGE_PROMPT_GENERATION_MODE=mock / llm`。
- `parse_image_prompt_llm_response` 已能校验 `ImagePromptOutput`。
- `tests/api` 当前已通过 44 passed。

## 3. Mimo 已知接入信息

- 官方文档入口：`https://platform.xiaomimimo.com/docs/zh-CN/welcome`
- OpenAI-compatible 请求地址：`https://api.xiaomimimo.com/v1/chat/completions`
- 当前额度：700,000,000 Credits
- 不记录真实 API Key。
- 当前实测：`sk-` 开头 API Key 可用于 ManJuFlow 后端直连 Mimo API。
- 当前实测：`tp-` 开头 Token Plan Key 直连 API 返回 `401 Invalid API Key`，后续更适合用于编程工具 / Agent 工具方向，不作为当前后端 API Key。

可用模型包括：

- `MiMo-V2.5-Pro`
- `MiMo-V2.5`
- `MiMo-V2.5-TTS-VoiceClone`
- `MiMo-V2.5-TTS-VoiceDesign`
- `MiMo-V2.5-TTS`
- `MiMo-V2-Pro`
- `MiMo-V2-Omni`
- `MiMo-V2-TTS`

模型名称在代码配置中建议使用小写官方 API 名称，例如如果官方要求为 `mimo-v2.5-pro`，则 `.env` 中使用：

```env
LLM_MODEL=mimo-v2.5-pro
```

实际模型名必须以官方控制台 / API 文档为准。

## 4. 推荐首轮测试模型

首轮测试建议使用 `mimo-v2.5-pro`。

原因：

- 第三阶段 ImagePrompt 需要结构化 JSON 输出能力。
- ImagePrompt 需要较好的视觉描述能力。
- ImagePrompt 需要较强的格式服从能力，输出必须匹配 `ImagePromptOutput`。

后续再对比：

- `mimo-v2.5`
- `mimo-v2-pro`

TTS 系列暂不接入当前文本生成链路，留到配音阶段评估。

## 5. 推荐接入方式

当前不建议大重构。

第一阶段 Mimo 接入方式已完成小样本验证：

- 复用现有 `LLMClient`。
- 通过 `.env` 临时切换：

```env
LLM_PROVIDER=mimo
MIMO_BASE_URL=https://api.xiaomimimo.com
MIMO_MODEL=mimo-v2.5-pro
MIMO_API_KEY=真实 sk token，不提交
IMAGE_PROMPT_GENERATION_MODE=llm
```

注意：

- 当前 `LLMClient` 内部拼接的是 `/v1/chat/completions`，因此 `MIMO_BASE_URL` 应配置为 `https://api.xiaomimimo.com`。
- 如果 `LLMClient` 要求完整 endpoint，则以当前代码实现为准。
- 当前推荐 ManJuFlow 后端直连 Mimo API 使用 `sk-` Key。
- `tp-` Key 后续可用于编程工具 / Agent 工具方向，不作为当前后端 API Key。

第二阶段再考虑：

- `DEEPSEEK_API_KEY`
- `MIMO_API_KEY`
- 多模型路由
- 不同模块指定不同模型

当前实测结果：

- `tp-` 开头 Token Plan Key 直连 API 返回 `401 Invalid API Key`
- `sk-` 开头 API Key 最小认证探测返回 200
- 最小认证探测返回 model 为 `mimo-v2.5-pro`
- 最小认证探测返回 content 为 `{"ok": true}`
- `sk-` Key 已成功用于 `/api/prompts/generate`
- `/api/prompts/generate` 已返回合法 `ImagePromptOutput`

## 6. 最小测试顺序

建议严格按顺序：

1. 不改代码，先确认当前 `LLMClient` 是否可通过 `.env` 切换到 Mimo；
2. 使用 `/api/prompts/generate` 做 ImagePrompt 小样本测试；
3. 确认返回合法 `ImagePromptOutput`；
4. 记录到 `docs/LLM_TEST_LOG.md`；
5. 再测试 `StoryboardOutput`；
6. 最后测试 `ScriptOutput`；
7. 绝不一开始就全链路大批量调用。

## 7. 安全与成本注意事项

- 不提交 `.env`。
- 不在日志或文档中记录真实 token。
- 测试后切回 `mock`。
- 先小样本，再批量。
- 利用非高峰期 16:00-24:00 UTC 0.8x 系数做大样本测试。
- TTS 免费期后续配音阶段再评估。
- 失败时优先保留 mock 稳定基线。

## 8. 当前暂不做

- 不做多 provider 大重构。
- 不接 TTS。
- 不接文生图。
- 不接 ComfyUI。
- 不做多 Agent。
- 不做批量任务系统。
- 不改前端 UI。

## 9. 下一步建议

- 检查当前 `LLMClient` 的 `base_url` 拼接方式。
- 确认 Mimo API model 名称大小写。
- 用 `.env` 临时切换 Mimo。
- 重启后端。
- curl 测试 `/api/prompts/generate`。
- 记录 `LLM_TEST_LOG`。
