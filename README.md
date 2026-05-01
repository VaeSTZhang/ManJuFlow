# ManJuFlow｜漫剧流 AI 影视化创作流水线平台

ManJuFlow｜漫剧流 是一个面向短剧、影视和视频内容生产的 AI 创作流水线原型。项目当前覆盖从灵感到结构化剧本、导演分镜、AI 绘图 Prompt 的核心链路，并为后续文生图、文生视频、配音字幕和成片输出预留扩展边界。

当前项目处于 actively developed prototype / MVP stage，不是最终生产系统。

## 项目定位

ManJuFlow 的目标是把内容生产流程拆成可验证、可替换、可迁移的小闭环：

```text
Idea
→ Script
→ Storyboard
→ ImagePrompt
→ 后续：Image / Video / Voice / Subtitle / Final Output
```

当前重点是完成前三个文本与结构化阶段，建立稳定的数据协议、Prompt 版本化、后端服务、前端闭环、测试体系和文档体系。

## 当前阶段成果

### Phase 1：Idea → Script

- 灵感输入
- 结构化短剧剧本输出
- FastAPI endpoint：`POST /api/scripts/generate`
- 前端展示、复制和导出 JSON
- mock / llm 模式基础能力

### Phase 2：Script → Storyboard

- 剧本转导演分镜
- 结构化 `StoryboardOutput`
- FastAPI endpoint：`POST /api/storyboards/generate`
- 前端分镜展示
- 剧本结果一键带入分镜生成
- 分镜 JSON 复制 / 导出

### Phase 3：Storyboard → ImagePrompt

- 分镜转 AI 绘图 Prompt
- 结构化 `ImagePromptOutput`
- FastAPI endpoint：`POST /api/prompts/generate`
- ImagePrompt mock / llm 模式
- ImagePrompt LLM parser
- 中文异常空格清洗
- DeepSeek / Mimo / Kimi / MiniMax 四家文本 LLM provider 接入
- 请求级 `llm_provider` / `llm_model` 选择
- 前端 ImagePrompt 模型选择器
- 绘图 Prompt JSON 复制 / 导出
- S001 四模型 ImagePrompt 对比已完成

## 当前能力清单

- 结构化剧本生成
- 结构化分镜生成
- AI 绘图 Prompt 生成
- mock / llm generation mode
- 多 LLM provider 配置
- 请求级 provider / model 选择
- 前端模型选择器
- JSON 复制 / 导出
- Pydantic Schema 校验
- Prompt 文件版本化
- LLM 输出解析与基础清洗
- 后端 API 测试
- 本地开发文档与模型对比文档

## 技术架构

```text
apps/
  api/                 FastAPI backend
    app/
      schemas/         Pydantic 数据协议
      services/        业务服务、LLMClient、parser、mock service
      prompts/         版本化 Prompt 文件
      routers/         API 路由
  web/                 React + Vite frontend

tests/
  api/                 后端 API / service / schema 测试
  fixtures/            标准样本与模型输出样例

docs/                  项目文档、阶段记录、API 契约、模型对比方案
scripts/               本地开发辅助脚本
```

## 支持的 LLM Providers

当前后端已支持以下 OpenAI-compatible 文本 LLM provider：

- DeepSeek
- Mimo / 小米大模型
- Kimi
- MiniMax

说明：

- API Key 通过本地 `.env` 配置。
- `.env` 不应提交到仓库。
- 公开仓库不包含任何真实密钥。
- 不传请求级 provider / model 时，后端使用 `.env` 中的默认 `LLM_PROVIDER`。
- ImagePrompt 请求可传 `llm_provider` / `llm_model` 做单次调用级覆盖。

## 本地启动方式

首次配置：

```bash
cp .env.example .env
```

后端启动：

```bash
bash scripts/dev_api.sh
```

如果 8000 端口被旧进程占用：

```bash
bash scripts/kill_api_port.sh
bash scripts/dev_api.sh
```

前端启动：

```bash
cd apps/web
npm install
npm run dev
```

访问地址：

- 后端健康检查：`http://127.0.0.1:8000/health`
- 后端接口文档：`http://127.0.0.1:8000/docs`
- 前端页面：`http://localhost:5173/`

## 测试与构建

后端测试：

```bash
python -m pytest tests/api
```

前端构建：

```bash
cd apps/web
npm run build
```

当前测试状态：

- `tests/api` 当前为 67 passed
- `npm run build` 已通过

## 环境变量说明

请参考 `.env.example` 创建本地 `.env`。

核心配置包括：

- `SCRIPT_GENERATION_MODE`
- `STORYBOARD_GENERATION_MODE`
- `IMAGE_PROMPT_GENERATION_MODE`
- `LLM_PROVIDER`
- `LLM_BASE_URL` / `LLM_MODEL` / `LLM_API_KEY`
- `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL` / `DEEPSEEK_API_KEY`
- `MIMO_BASE_URL` / `MIMO_MODEL` / `MIMO_API_KEY`
- `KIMI_BASE_URL` / `KIMI_MODEL` / `KIMI_API_KEY`
- `MINIMAX_BASE_URL` / `MINIMAX_MODEL` / `MINIMAX_API_KEY`

建议默认保持：

```env
SCRIPT_GENERATION_MODE=mock
STORYBOARD_GENERATION_MODE=mock
IMAGE_PROMPT_GENERATION_MODE=mock
```

`llm` 模式会调用真实模型，需要本地自行配置 API Key。公开仓库不会提供任何真实密钥。

## 文档导航

- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [Phase 3 Progress](docs/PHASE_3_PROGRESS.md)
- [API Contract](docs/API_CONTRACT.md)
- [Local Development](docs/LOCAL_DEV.md)
- [Model Comparison Plan](docs/MODEL_COMPARISON_PLAN.md)
- [Model Comparison Results](docs/MODEL_COMPARISON_RESULTS.md)
- [Model Comparison Runbook](docs/MODEL_COMPARISON_RUNBOOK.md)

## Roadmap

以下内容属于后续规划，尚未作为生产能力完成：

- 第四阶段：文生图 / 远端 GPU / ComfyUI
- 第五阶段：文生视频 / 图生视频
- 第六阶段：资产管理 / 任务系统
- 第七阶段：配音 / 字幕 / BGM / 成片合成
- 第八阶段：部署 / 产品化 / 商业化

## 安全说明

- 不提交 API Key。
- 不提交 `.env`。
- 不提交真实客户数据。
- 不提交合作方敏感信息。
- 不在代码、文档、日志或测试样例中写入真实密钥。
- 真实部署需要单独配置环境变量、密钥管理、权限控制和数据隔离。

## 项目状态声明

ManJuFlow 当前是公开可评审的 MVP 原型项目，重点展示架构、数据协议、流水线闭环、多模型接入方式、测试覆盖和后续可扩展方向。

该项目仍在持续开发中，文生图、文生视频、配音字幕、资产管理、任务队列和生产部署等能力将在后续阶段逐步推进。
