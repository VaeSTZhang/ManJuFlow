# ManJuFlow｜漫剧流

AI 影视化创作流水线平台｜从灵感、剧本、分镜、绘图 Prompt 到图像生成的模块化创作工作台

A modular AI cinematic content creation pipeline for script, storyboard, image prompt and image generation workflows.

![Phase](https://img.shields.io/badge/Phase-4%20Image%20Generation%20Mock-2563eb)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![Schema](https://img.shields.io/badge/Schema-Pydantic-e92063)
![Mode](https://img.shields.io/badge/Mode-Mock%20%2F%20LLM-0f766e)
![License](https://img.shields.io/badge/License-No%20public%20license%20yet-b42318)

ManJuFlow｜漫剧流 是一个面向短剧、影视和视频内容生产的 AI 创作流水线 MVP。它把从创意灵感到结构化剧本、导演分镜、AI 绘图 Prompt、mock 图片生成的前期创作链路组织成可验证、可交接、可迁移的工程闭环。

当前公开仓库重点展示数据协议、mock demo、接口边界、前端工作台、测试体系和私有部署安全边界。它不是最终生产系统，也不包含真实 ComfyUI / GPU 部署配置。

## Why ManJuFlow

AI 影视生产流程常见的问题是链路割裂：创意、剧本、分镜、Prompt、图像生成分散在不同工具中，结果难追踪，Prompt 难复用，非技术团队使用门槛高。

ManJuFlow 的目标是把这些步骤拆成稳定的小闭环：

- 每一步都有结构化 Schema；
- 每一步输出都能作为下一步输入；
- mock 模式支持本地评审和演示；
- LLM / provider 接入保持可替换；
- 公开仓库和私有部署边界清晰；
- 合作方技术员和未来接手开发者可以快速理解工程结构。

## Current Pipeline

```text
IdeaInput
  -> ScriptOutput
  -> StoryboardOutput
  -> ImagePromptOutput
  -> ImageGenerationOutput mock
  -> Future ComfyUI / Video / Post-production
```

## Current Capabilities

| Area | Status | Notes |
| --- | --- | --- |
| Phase 1 Idea → Script | 已完成 | 结构化短剧剧本生成，支持前端展示、复制、导出 |
| Phase 2 Script → Storyboard | 已完成 | 导演分镜 Schema、mock service、API 和前端闭环 |
| Phase 3 Storyboard → ImagePrompt | 已完成 | 绘图 Prompt Schema、mock / llm、parser、前端模型选择器 |
| Phase 4 ImagePrompt → ImageGeneration | 已完成 mock 闭环 | Schema、mock service、endpoint、前端 mock image card |
| Multi LLM Provider | 已接入 | DeepSeek / Mimo / Kimi / MiniMax 文本 provider |
| Model Comparison | 进行中 | S001 四模型 ImagePrompt 对比已完成 |
| ComfyUI | 安全占位 | provider interface / placeholder / private deployment runbook |
| Frontend | 本地可运行 | React + Vite 工作台，覆盖核心创作链路 |
| Tests | 持续维护 | 后端 `tests/api` 覆盖 schema / service / endpoint / parser |
| Docs | 已建立 | API 契约、本地开发、阶段总结、合作边界、私有部署草案 |

## Architecture Overview

```text
apps/
  api/                         FastAPI backend
    app/
      schemas/                 Pydantic data contracts
      services/                business services, providers, parser, mock logic
      prompts/                 versioned prompt templates
      routers/                 API endpoints
  web/                         React + Vite frontend

tests/
  api/                         backend schema / service / endpoint tests
  fixtures/                    stable samples and model output examples

docs/                          project docs, API contracts, phase plans, runbooks
scripts/                       local development helper scripts
```

## Data Contract First

ManJuFlow 使用结构化数据协议作为 AI 流水线边界。核心对象包括：

- `IdeaInput`
- `ScriptOutput`
- `StoryboardOutput`
- `ImagePromptOutput`
- `ImageGenerationOutput`

每一步都尽量避免只返回不可控文本，而是返回可校验、可展示、可复制、可导出、可继续传递给下一阶段的数据结构。

## API Overview

当前主要 API：

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | 后端健康检查 |
| GET | `/api/system/status` | 当前系统与生成模式状态 |
| POST | `/api/scripts/generate` | 灵感生成结构化剧本 |
| POST | `/api/storyboards/generate` | 剧本生成导演分镜 |
| POST | `/api/prompts/generate` | 分镜生成 AI 绘图 Prompt |
| POST | `/api/images/generate` | 绘图 Prompt 生成 mock 图片结果 |

详细字段请看 [API Contract](docs/API_CONTRACT.md)。

## Quick Start

Adjust paths to your local clone when needed.

Backend:

```bash
cd /Users/zhangtritsen/Desktop/Code/ManJuFlow
bash scripts/dev_api.sh
```

If port `8000` is already in use:

```bash
bash scripts/kill_api_port.sh
bash scripts/dev_api.sh
```

Frontend:

```bash
cd apps/web
npm run dev
```

Open:

- Backend health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`
- Web app: `http://localhost:5173/`

Backend tests:

```bash
python -m pytest tests/api
```

Frontend build:

```bash
cd apps/web
npm run build
```

## Image Generation / ComfyUI Boundary

Current state:

- `/api/images/generate` is mock only.
- It does not call real ComfyUI.
- It does not require remote GPU.
- It does not generate real image files.
- `mock_url` is a stable placeholder path for UI and contract validation.
- `ComfyUIImageGenerationProviderPlaceholder` exists only as an extension boundary.

Future real ComfyUI integration must live in a private deployment environment. The following must not be committed to this public repository:

- real workflow files;
- real server URLs;
- auth tokens or API keys;
- model weights or model paths;
- customer assets;
- production outputs.

Future workflow design must support multiple workflow names, versions, presets, and registry mapping. `workflow_name` is a logical name, not a private workflow file path.

Expected future concepts:

- `workflow_name`
- `workflow_version`
- `workflow_preset`
- `workflow_parameters`
- private workflow registry
- provider adapter normalization

## Public Repository Safety Boundary

This public repository can contain:

- Schema;
- mock service;
- mock endpoint;
- provider interface;
- ComfyUI placeholder;
- docs and runbooks;
- safe examples;
- local demo code.

This public repository must not contain:

- API Key;
- `.env`;
- SSH Key;
- real server address;
- private ComfyUI workflow;
- model weights;
- customer data;
- partner confidential materials;
- production output assets.

## Usage Notice / License Notice

当前仓库暂未授予开源许可证。

公开访问仅用于技术评审、项目展示、合作沟通和架构讨论。未经项目所有者书面许可，不得将本仓库或其中任何代码、文档、Prompt、Schema、架构设计用于商业使用、再分发、转授权、生产部署或作为第三方项目资产使用。

Public visibility does not imply open-source authorization.

This repository is currently published for technical review, demonstration, and collaboration discussion only. No open-source license has been granted yet. Commercial use, redistribution, sublicensing, production deployment, or incorporation into third-party project assets requires prior written permission from the project owner.

## Roadmap

Near-term:

- ComfyUI provider design;
- workflow registry / preset mapping;
- private ComfyUI small-sample integration checklist;
- `.env.example` placeholder refinement;
- README and docs polish;
- UI information architecture cleanup.

Mid-term:

- asset manager;
- task center;
- image-to-video;
- TTS / subtitles / BGM;
- post-production / FFmpeg;
- Docker and deployment later.

Long-term:

- private deployment templates;
- production task queue;
- storage and permission model;
- collaboration and review workflows;
- commercial productization after legal and business terms are clear.

## Documentation Index

- [API Contract](docs/API_CONTRACT.md)
- [Local Development](docs/LOCAL_DEV.md)
- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [Phase 3 Summary](docs/PHASE_3_SUMMARY.md)
- [Phase 4 Image Generation Plan](docs/PHASE_4_IMAGE_GENERATION_PLAN.md)
- [ComfyUI Private Deployment Runbook Draft](docs/COMFYUI_PRIVATE_DEPLOYMENT_RUNBOOK_DRAFT.md)
- [Cooperation Tech Asset Boundary Draft](docs/COOPERATION_TECH_ASSET_BOUNDARY_DRAFT.md)
- [Model Comparison Results](docs/MODEL_COMPARISON_RESULTS.md)

## Project Status

ManJuFlow is currently in active MVP development. The public repository focuses on reviewable architecture, local mock demos, data contracts, and safe integration boundaries.

It is not a final production system. Real ComfyUI, remote GPU, customer assets, private workflows, model weights, production storage, and deployment credentials belong in private environments only.
