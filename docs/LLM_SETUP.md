# Dramora｜剧作工坊真实 LLM 接入配置说明

ManJuFlow 是早期工程代号。当前配置说明以 Dramora 仓库和项目根目录 `.env` 为准。

## 当前默认模式

当前后端默认使用 mock 模式：

```text
SCRIPT_GENERATION_MODE=mock
ASSISTANT_GENERATION_MODE=mock
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

后端会通过 OpenAI-compatible Chat Completions API 调用模型。通用 fallback 请求路径格式为：

```text
POST {LLM_BASE_URL}/v1/chat/completions
```

当前代码已具备基础调用能力，但真实 LLM 模式仍需要进一步测试输出稳定性。

## 环境变量说明

真实配置文件统一放在项目根目录 `.env`，可以从模板创建：

```bash
cp .env.example .env
```

不再需要 `apps/api/.env`。后端从 `apps/api` 启动时，也会读取项目根目录 `.env`。
`.env.example` 是唯一公开模板，只放字段名和安全占位值；真实 API Key 不提交。

本地 `.env` 示例：

```text
APP_ENV=local
SCRIPT_GENERATION_MODE=llm
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_SCRIPT_MODEL=deepseek-chat
LLM_REQUEST_TIMEOUT_SECONDS=60
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_API_KEY=只写入本地真实密钥，不要提交
```

说明：

- `SCRIPT_GENERATION_MODE`：剧本生成模式，支持 `mock` 或 `llm`
- `ASSISTANT_GENERATION_MODE`：历史兼容字段；当前版本不规划右侧聊天式 AI Assistant，不新增 assistant 专用配置
- `DEFAULT_LLM_PROVIDER`：后端默认 provider；当前推荐 `deepseek`
- `DEFAULT_SCRIPT_MODEL`：后端默认剧本生成模型；当前推荐 `deepseek-chat`
- `LLM_REQUEST_TIMEOUT_SECONDS`：默认 LLM 请求超时时间
- `LLM_PROVIDER` / `LLM_BASE_URL` / `LLM_MODEL` / `LLM_API_KEY`：保留为兼容字段和通用 OpenAI-compatible fallback
- `DEEPSEEK_*` / `MIMO_*` / `KIMI_*` / `MINIMAX_*`：各 provider 的独立配置字段

`/api/system/status` 中的 `llm_enabled` 会根据 `DEFAULT_LLM_PROVIDER` 对应的 provider API Key 判断。默认推荐 DeepSeek 时，只需要配置 `DEEPSEEK_API_KEY` 即可让 `llm_enabled=true`；不需要同时维护 `LLM_API_KEY`。`LLM_API_KEY` 仅作为 legacy / fallback OpenAI-compatible key 保留。

## 安全提醒

- 不要把真实 `.env` 提交到 Git
- `.env` 统一放在项目根目录
- 不要创建或依赖 `apps/api/.env`
- 不要把 API Key 写进代码
- 不要把 API Key 发给任何 AI
- `.env.example` 只放字段名，不放真实值
- 真实配置只维护根目录 `.env` 一个文件，不要出现“两个文件同时修改才生效”的流程
- 如果怀疑 API Key 泄露，应立即在服务商后台撤销并重新生成

## 本地测试流程

1. 在项目根目录创建本地 `.env` 文件：

```bash
cp .env.example .env
```

2. 填入真实 API Key 和模型配置：

```text
SCRIPT_GENERATION_MODE=llm
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_SCRIPT_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_API_KEY=这里填本地真实密钥，不要提交
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

DeepSeek 是当前默认推荐模型，但不应在业务代码中写死。Mimo / Kimi / MiniMax 等 provider 可通过统一 LLM 配置扩展。以下只展示字段示例，不包含真实 Key：

```text
SCRIPT_GENERATION_MODE=llm
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_SCRIPT_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_API_KEY=不要写入真实密钥
```

后端默认配置以 `DEFAULT_LLM_PROVIDER` / `DEFAULT_SCRIPT_MODEL` 为当前推荐入口；请求级模型选择通过 `AIRequestOptions` 传递，后续剧本生成、电影剧本改编、小说 / 网文改编、扩写、质量评审、分镜 / Prompt 生成应复用同一结构。当前版本不规划右侧聊天式 AI Assistant，也不新增 assistant 专用 provider / model / key 配置；这不代表取消其他 LLM provider，不要在业务代码中硬编码 DeepSeek。

系统状态检查：

- `GET /api/system/status` 会返回 `llm_enabled`；
- `llm_enabled` 基于 `DEFAULT_LLM_PROVIDER` 对应 key 判断；
- `DEFAULT_LLM_PROVIDER=deepseek` 时检查 `DEEPSEEK_API_KEY`；
- `LLM_API_KEY` 只作为 legacy / fallback key，不要求和 `DEEPSEEK_API_KEY` 同时配置。

## 当前限制

- 真实 LLM 模式尚未经过生产验证
- 需要进一步测试 JSON 输出稳定性
- 模型可能返回 Markdown、解释文字或不完整 JSON，需要继续优化 Prompt 和解析策略
- 未来可能接 LiteLLM 做统一模型网关
