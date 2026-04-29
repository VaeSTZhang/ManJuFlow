# ManJuFlow｜漫剧流真实 LLM 接入配置说明

## 当前默认模式

当前后端默认使用 mock 模式：

```text
SCRIPT_GENERATION_MODE=mock
```

在 mock 模式下：

- 不调用真实模型
- 不需要配置 API Key
- 适合本地演示
- 适合前端联调
- `/api/scripts/generate` 会返回稳定的 mock 结构化剧本结果

## 未来真实 LLM 模式

未来需要接入真实模型时，可以切换为：

```text
SCRIPT_GENERATION_MODE=llm
```

后端会通过 OpenAI-compatible Chat Completions API 调用模型，请求路径格式为：

```text
POST {LLM_BASE_URL}/v1/chat/completions
```

当前代码已具备基础调用能力，但真实 LLM 模式仍需要进一步测试输出稳定性。

## 环境变量说明

本地 `.env` 示例：

```text
SCRIPT_GENERATION_MODE=llm
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_API_KEY=不要写入真实密钥
```

说明：

- `SCRIPT_GENERATION_MODE`：剧本生成模式，支持 `mock` 或 `llm`
- `LLM_BASE_URL`：OpenAI-compatible API Base URL
- `LLM_MODEL`：模型名称
- `LLM_API_KEY`：模型服务 API Key

## 安全提醒

- 不要把真实 `.env` 提交到 Git
- 不要把 API Key 写进代码
- 不要把 API Key 发给任何 AI
- `.env.example` 只放字段名，不放真实值
- 如果怀疑 API Key 泄露，应立即在服务商后台撤销并重新生成

## 本地测试流程

1. 在 `apps/api` 目录下创建本地 `.env` 文件。

2. 填入真实 API Key 和模型配置：

```text
SCRIPT_GENERATION_MODE=llm
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_API_KEY=这里填本地真实密钥，不要提交
```

3. 启动后端：

```bash
cd apps/api
uvicorn app.main:app --reload
```

4. 调用 `/api/scripts/generate`：

```bash
curl -X POST http://127.0.0.1:8000/api/scripts/generate \
  -H "Content-Type: application/json" \
  -d '{"idea_text":"一个被裁员的中年男人，意外发现公司老板用 AI 伪造财报","script_type":"短剧","genre":"都市悬疑"}'
```

5. 检查返回结果是否符合 `ScriptOutput` JSON 结构。

如果模型返回不是合法 JSON，需要回到 `apps/api/app/prompts/idea_to_script_v1.md` 或解析逻辑中修复。

## DeepSeek 示例配置

以下只展示字段示例，不包含真实 Key：

```text
SCRIPT_GENERATION_MODE=llm
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_API_KEY=不要写入真实密钥
```

## 当前限制

- 真实 LLM 模式尚未经过生产验证
- 需要进一步测试 JSON 输出稳定性
- 模型可能返回 Markdown、解释文字或不完整 JSON，需要继续优化 Prompt 和解析策略
- 未来可能接 LiteLLM 做统一模型网关
