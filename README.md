# ManJuFlow｜漫剧流

AI-powered short-drama script generation and adaptation workbench.

面向编剧、短剧策划、漫剧内容团队的 AI 短剧剧本生成与改编工作台。

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

This default README is a concise bilingual landing page. For full project details, use the language-specific pages above.

当前默认 README 是简洁双语入口页。完整项目说明请进入上方中文或英文主页。

## Project Overview

ManJuFlow is currently being redesigned as a three-entry AI short-drama script generation and adaptation workbench. It helps creative teams transform ideas, film scripts, or novels into editable short-drama scripts.

ManJuFlow 当前主线是三入口短剧剧本生成与改编：灵感生成短剧剧本、电影剧本改编短剧剧本、小说改编短剧剧本。生成后可继续在线编辑、导出、上传修改稿，并在后续进入短剧剧本切分 / 分镜 / Prompt。

Current focus: **Phase 5 Three-entry Short-drama Script Workbench**.

当前重点：**第五阶段｜三入口短剧剧本生成与改编工作台**。

## Current Capabilities

- **Phase 1: Idea → Script**  
  灵感输入生成结构化短剧剧本。
- **Phase 2: Script → Storyboard**  
  剧本生成导演分镜。
- **Phase 3: Storyboard → Image Prompt**  
  分镜生成 AI 绘图 Prompt，支持 Prompt 中文 / 英文输出。
- **Phase 4: Image Prompt → Image Generation Mock / Asset / Task / Workspace**  
  图片生成 mock、Bundle、Asset、RenderTask 和工作台 UI。
- **Phase 5: Three-entry Short-drama Script Workbench**  
  三入口重整：灵感生成短剧、电影剧本改短剧、小说改短剧。电影 / 小说改编仍处于规划和 mock 优先推进阶段。

Current primary entries:

- Idea to Short Drama Script｜灵感生成短剧剧本
- Film Script to Short Drama｜电影剧本改编短剧剧本
- Novel to Short Drama｜小说改编短剧剧本

Next major feature after script generation:

- Script Segmentation / Storyboard / ImagePrompt｜短剧剧本切分 / 分镜 / Prompt

Image generation and video generation are not the current market-trial focus.

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
Login / Mock Login
  -> Choose Creation Entry
  -> Idea / Film Script / Novel
  -> Short-drama Script
  -> Online Edit / Export / Upload Revision
  -> Next: Segmentation / Storyboard / Prompt
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

The project is under active development. Current focus: **Phase 5 Three-entry Short-drama Script Workbench**.

项目正在持续开发中，当前重点是第五阶段“三入口短剧剧本生成与改编工作台”。

For cooperation or technical review, please start with [README.zh-CN.md](README.zh-CN.md) or [README.en.md](README.en.md).
