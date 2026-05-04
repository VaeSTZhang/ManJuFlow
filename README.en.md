# Dramora

[Chinese](README.zh-CN.md) | [English](README.en.md)

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)
![Schema](https://img.shields.io/badge/Schema-Pydantic-e92063)
![Mode](https://img.shields.io/badge/Mode-Mock--first-0f766e)

## Product Positioning

**Dramora｜剧作工坊** is a cinematic script workbench for transforming ideas and source texts into structured short-drama scripts.

The current product focus is script creation and text adaptation. It is not positioned as an image generation, video generation, or automated film production system at this stage.

Dramora is designed for writers, short-drama planners, manhua-style content teams, and creative operators who need an editable and reviewable script workflow before downstream media generation.

The local engineering directory and early internal project codename remain `ManJuFlow`. This brand update does not rename local paths, scripts, backend packages, frontend package names, or API paths.

## Core Workflows

### Idea Generation

Generate a structured short-drama script from story ideas, character relationships, or hook-driven concepts.

Best for:

- original short-drama concepts;
- early story validation;
- character relationship drafts;
- quick editable episode outlines.

### Text Adaptation

Adapt film scripts, novels, web fiction, or long-form story text into short-drama pacing.

Best for:

- film script to short-drama adaptation;
- long script compression;
- novel / web fiction adaptation;
- source text organization before further creative work.

## Current Frontend Information Architecture

```text
Login
  -> Script Creation
      -> Idea Generation
      -> Text Adaptation
          -> Film Script Adaptation
          -> Novel / Web Fiction Adaptation
  -> Script Adaptation
      -> Long-text organization and short-drama adaptation
```

Storyboarding, prompt generation, image generation, assets, and tasks remain in the engineering foundation, but they are not emphasized in the current boss-demo and market-trial main interface.

## Engineering Foundation

- FastAPI backend;
- Pydantic data contracts;
- React + Vite + TypeScript frontend;
- AppShell / Sidebar / Toast workbench foundation;
- Idea-to-script baseline workflow;
- Text organization / script adaptation workspace;
- Mock Word script upload;
- input limits and backend validation;
- frontend-friendly API error display;
- Document Export Schema;
- three-entry short-drama generation schema / registry / mock service / endpoint foundation;
- mock-first local demonstration strategy.

## Technical Architecture

Backend:

- Python;
- FastAPI;
- Pydantic;
- `schemas` / `services` / `routers`;
- versioned prompt files;
- OpenAI-compatible `LLMClient`;
- mock / llm generation modes;
- pytest coverage.

Frontend:

- React;
- Vite;
- TypeScript;
- AppShell;
- Sidebar;
- script creation home;
- script adaptation workspace;
- Chinese-first UI;
- browse-before-login and operate-after-login demonstration gate.

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

Do not commit `.env`, API keys, customer scripts, real server addresses, or sensitive cooperation materials.

## Project Structure

```text
ManJuFlow/
├── apps/
│   ├── api/
│   │   └── app/
│   │       ├── schemas/
│   │       ├── services/
│   │       ├── routers/
│   │       └── prompts/
│   └── web/
│       └── src/
│           ├── api/
│           ├── types/
│           ├── components/
│           └── App.tsx
├── docs/
├── examples/
├── scripts/
├── tests/
└── README.md
```

## Documentation

- [API Contract](docs/API_CONTRACT.md)
- [Local Development](docs/LOCAL_DEV.md)
- [Roadmap](docs/MVP_ROADMAP.md)
- [Project Structure Plan](docs/PROJECT_STRUCTURE_REFACTOR_PLAN.md)
- [Repository Boundary Draft](docs/COOPERATION_TECH_ASSET_BOUNDARY_DRAFT.md)

## Repository Boundary and Rights Notice

This public repository is intended for:

- technical review;
- project demonstration;
- collaboration discussion.

No public open-source license has been granted. Public visibility does not mean open-source authorization. Commercial use, redistribution, sublicensing, or production deployment is not permitted without written permission.

This repository must not contain:

- real API keys;
- `.env` files;
- real customer scripts;
- real employee data;
- real server addresses;
- private workflows;
- model weights;
- production databases;
- sensitive cooperation materials.
