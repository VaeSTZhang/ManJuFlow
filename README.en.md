# Dramora

[Chinese](README.zh-CN.md) | [English](README.en.md)

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)
![Schema](https://img.shields.io/badge/Schema-Pydantic-e92063)
![Status](https://img.shields.io/badge/Status-Internal%20Development-2563eb)

## Product Positioning

**Dramora｜剧作工坊** is a cinematic script workbench for transforming ideas and source texts into structured short-drama scripts.

The current product focus is script creation and text adaptation. It is not positioned as an image generation, video generation, or automated film production system at this stage.

Dramora is designed for writers, short-drama planners, manhua-style content teams, and creative operators who need an editable and reviewable script workflow before downstream media generation.

`ManJuFlow` was the early internal project codename. The public repository and local engineering directory now use `Dramora`; scripts, backend packages, frontend package names, and API paths are not renamed as part of the brand update.

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

## Current Status

Dramora currently focuses on an internal script generation and adaptation workbench:

- three-entry script creation flow: `idea`, `film_script`, and `novel`;
- real DeepSeek LLM smoke acceptance completed for all three entries;
- the `film_script` `target_episode_count` issue has been guarded by prompt tuning and backend contract validation;
- generated results use a unified `ShortDramaScriptOutput`;
- the frontend supports review, basic editing, and TXT / JSON / DOCX export;
- real `.docx` import preview is wired into the frontend, with user confirmation before filling or appending source text;
- `context_options` now tracks the first layer of user / workspace / project / session ownership;
- first-layer internal auth is wired: frontend login now calls the backend auth API, still using safe in-memory test users, not production-grade authorization;
- Usage Ledger now has a SQLite repository and is wired into script generation, document import preview, and TXT / JSON / DOCX export; it stores redacted summaries only, not full text, uploaded files, raw model responses, or secrets.
- The first round of frontend App structure refactoring is complete: `App.tsx` was reduced from 2167 to 1465 lines by extracting Toast, Auth, Workspace Navigation, Legacy Idea, Storyboard, Image Prompt, and Image Generation hooks.

Deployment has not started yet. Dramora is not presented as production-ready, commercially deployed, or backed by a completed multi-user permission system.
The frontend is not claimed to be structurally perfect, but this refactor lowers the maintenance risk for the next phase.

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

Storyboarding, prompt generation, image generation, assets, and tasks remain in the engineering foundation as the next major workflow, but they are currently deferred from the main boss-demo and market-trial interface.

## Engineering Foundation

- FastAPI backend;
- Pydantic data contracts;
- React + Vite + TypeScript frontend;
- AppShell / Sidebar / Toast workbench foundation;
- Idea-to-script baseline workflow;
- Text organization / script adaptation workspace;
- real `.docx` Word import preview and user confirmation flow;
- input limits and backend validation;
- frontend-friendly API error display;
- Document Import / Export schemas, services, and endpoints;
- DOCX export service and file download endpoint;
- three-entry short-drama generation schemas, prompts, services, and endpoint;
- ContextOptions ownership foundation;
- Usage Ledger SQLite persistence with redacted summary records;
- first-round frontend App structure refactor;
- Playwright e2e smoke coverage.

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
cd /path/to/Dramora
bash scripts/dev_api.sh
```

Frontend:

```bash
cd /path/to/Dramora/apps/web
npm run dev
```

Backend tests:

```bash
cd /path/to/Dramora
python -m pytest tests/api
```

Frontend build:

```bash
cd /path/to/Dramora/apps/web
npm run build
```

Do not commit `.env`, API keys, customer scripts, real server addresses, or sensitive cooperation materials.
The public repository also excludes generated builds, local virtual environments, uploaded files, test reports, local storage, and production configuration.

## Project Structure

```text
Dramora/
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
