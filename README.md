# ManJuFlow｜漫剧流

AI-powered cinematic creation workflow platform for short drama, manhua-style storytelling, storyboards, visual prompts, and media generation pipelines.

面向短剧 / 漫剧 / AI 影视化创作的模块化流水线工作台。

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)
![Python](https://img.shields.io/badge/Backend-Python-3776ab)
![Status](https://img.shields.io/badge/Status-MVP%20%2F%20In%20Development-2563eb)
![License](https://img.shields.io/badge/License-No%20public%20license%20yet-b42318)

## Language

| 中文 | English |
| --- | --- |
| [中文文档](README.zh-CN.md) | [English Docs](README.en.md) |

## Project Overview

ManJuFlow is a modular AI cinematic creation workflow platform. It helps transform ideas or existing scripts into structured scripts, storyboards, AI image prompts, and media-generation-ready assets.

ManJuFlow 用于将灵感或已有剧本逐步转化为结构化剧本、导演分镜、AI 绘图 Prompt，以及后续媒体生成链路所需的资产与任务结构。

Current focus: **Phase 5 Text-to-Prompt Workbench**.

当前重点：**第五阶段｜文字到媒体提示词工作台**。

## Current Capabilities

- **Phase 1: Idea → Script**  
  灵感输入生成结构化剧本。
- **Phase 2: Script → Storyboard**  
  剧本生成导演分镜。
- **Phase 3: Storyboard → Image Prompt**  
  分镜生成 AI 绘图 Prompt，支持 Prompt 中文 / 英文输出。
- **Phase 4: Image Prompt → Image Generation Mock / Asset / Task / Workspace**  
  图片生成 mock、Bundle、Asset、RenderTask 和工作台 UI。
- **Phase 5: Text-to-Prompt Workbench**  
  已有剧本切分、Upload Mock、Workspace Context Isolation、Assistant Planning。

## Why ManJuFlow

- Modular workflow；
- Structured JSON / Pydantic data contracts；
- Prompt versioning；
- Mock-first development；
- Frontend-first usability；
- Private deployment boundary；
- Designed for non-technical content teams；
- Safe public repository boundary。

中文概括：

- 模块化创作链路；
- 数据协议优先；
- Prompt 版本化；
- mock 优先；
- 前端可用性优先；
- 公开仓库与私有部署边界清晰；
- 面向非技术内容团队；
- 不在公开仓库暴露敏感生产资料。

## Workflow Overview

```text
Idea / Existing Script
  -> Script / Segments
  -> Storyboard
  -> Image Prompt
  -> Image Generation Mock / Bundle
  -> Assets / Render Tasks
```

## Repository Structure

- `apps/api`：FastAPI backend
- `apps/web`：React + Vite frontend
- `docs`：architecture, phase plans, runbooks
- `tests/api`：backend tests
- `scripts`：local dev scripts
- `examples`：safe example inputs / outputs

## Local Development

Quick start:

```bash
cd /path/to/ManJuFlow
bash scripts/dev_api.sh
```

Frontend:

```bash
cd /path/to/ManJuFlow/apps/web
npm run dev
```

Backend tests:

```bash
cd /path/to/ManJuFlow
python -m pytest tests/api
```

Frontend build:

```bash
cd /path/to/ManJuFlow/apps/web
npm run build
```

For complete setup details, see [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md).

## Quick Navigation

- [中文 README](README.zh-CN.md)
- [English README](README.en.md)
- [docs](docs/)
- [apps/api](apps/api/)
- [apps/web](apps/web/)
- [tests/api](tests/api/)
- [API Contract](docs/API_CONTRACT.md)
- [MVP Roadmap](docs/MVP_ROADMAP.md)

## Repository Boundary / Usage Notice

This public repository is currently provided for technical review, project demonstration, and cooperation discussion only.

No open-source license has been granted yet. Public visibility does not mean open-source authorization. Without written permission, commercial use, redistribution, sublicensing, or production deployment is not permitted.

Real API keys, server addresses, model weights, customer data, private ComfyUI workflows, private workflow registries, and sensitive cooperation materials are not included in this repository.

当前公开仓库仅用于技术评审、项目展示和合作沟通。

暂未授予开源许可证。公开可见不等于开源授权。未经书面许可，不得商业使用、再分发、转授权或生产部署。

真实 API Key、服务器地址、模型权重、客户数据、私有 ComfyUI workflow、私有 workflow registry、合作敏感资料不进入公开仓库。

## Development Status

The project is under active development. Current focus: **Phase 5 Text-to-Prompt Workbench**.

项目正在持续开发中，当前重点是第五阶段“文字到媒体提示词工作台”。

For cooperation or technical review, please start with [README.zh-CN.md](README.zh-CN.md) or [README.en.md](README.en.md).
