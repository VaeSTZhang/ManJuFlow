# Dramora｜剧作工坊

A cinematic script workbench for transforming ideas and source texts into structured short-drama scripts.

面向短剧创作的结构化剧本生成与文本改编工作台。

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)
![Python](https://img.shields.io/badge/Backend-Python-3776ab)
![Status](https://img.shields.io/badge/Status-In%20Development-2563eb)
![License](https://img.shields.io/badge/License-No%20public%20license%20yet-b42318)

## Language

| 中文 | English |
| --- | --- |
| [中文文档](README.zh-CN.md) | [English Docs](README.en.md) |

## Project Overview

Dramora is a short-drama script generation and text adaptation workbench for writers, short-drama planners, and content teams. It focuses on two core workflows:

- Idea to short-drama script;
- Source text adaptation, including film scripts, novels, web fiction, and long-form story text.

Dramora 当前聚焦“剧本创作生成”：从故事灵感、人物关系、电影剧本、小说或网文文本出发，生成适合短剧创作的结构化剧本。分镜、Prompt、图片生成等后续流程保留为后续能力，不作为当前老板演示主界面重点。

ManJuFlow remains the local engineering directory and early internal project codename. Package names, local scripts, backend module names, and API paths are not renamed in this brand update.

## Current Product Focus

```text
Login
  -> Script Creation
  -> Idea Generation / Text Adaptation
  -> Editable Short-drama Script
  -> Export / Document Round-trip
```

Primary product entries:

- **灵感生成**：从故事灵感、人物关系或爽点方向生成短剧剧本。
- **文本改编**：将电影剧本、小说、网文或长文本改编成短剧节奏。

## Why Dramora

- Focused on script creation before downstream media generation;
- Designed for non-technical writing and content teams;
- Structured data contracts and editable outputs;
- Mock-first engineering loops before private deployment;
- Clear boundary between public repository and private production assets.

## Local Development

Use your own local clone path.

Backend:

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

## Quick Navigation

- [中文 README](README.zh-CN.md)
- [English README](README.en.md)
- [docs](docs/)
- [apps/api](apps/api/)
- [apps/web](apps/web/)
- [tests/api](tests/api/)
- [API Contract](docs/API_CONTRACT.md)
- [Roadmap](docs/MVP_ROADMAP.md)

## Repository Boundary / Usage Notice

This public repository is currently provided for technical review, project demonstration, and cooperation discussion only.

No public open-source license has been granted. Public visibility does not mean open-source authorization. Without written permission, commercial use, redistribution, sublicensing, or production deployment is not permitted.

Real API keys, `.env` files, server addresses, model weights, customer scripts, employee data, private workflows, private workflow registries, and sensitive cooperation materials are not included in this repository.

当前公开仓库仅用于技术评审、项目展示和合作沟通。

当前暂未授予开源许可证。公开可见不等于开源授权。未经书面许可，不得商业使用、再分发、转授权或生产部署。

真实 API Key、`.env`、服务器地址、模型权重、客户剧本、员工数据、私有 workflow、私有 workflow registry、合作敏感资料不进入公开仓库。

## GitHub About

Recommended description:

```text
A cinematic script workbench for transforming ideas and source texts into structured short-drama scripts.
```

中文说明：

```text
面向短剧创作的结构化剧本生成与文本改编工作台。
```
