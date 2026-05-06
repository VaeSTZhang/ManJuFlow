# Dramora｜剧作工坊

[中文](README.zh-CN.md) | [English](README.en.md)

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)
![Schema](https://img.shields.io/badge/Schema-Pydantic-e92063)
![Status](https://img.shields.io/badge/Status-Internal%20Development-2563eb)

## 产品定位

**Dramora｜剧作工坊** 是面向短剧创作的结构化剧本生成与文本改编工作台。

当前产品重点是“剧本创作生成”，而不是直接做文生图、文生视频或自动成片。它服务编剧、短剧策划、漫剧内容团队和内容运营人员，帮助用户从一句灵感、一段电影剧本或一篇小说文本出发，生成可编辑、可导出、可继续加工的短剧剧本。

`ManJuFlow` 是早期工程代号。当前公开仓库和本地工程目录统一使用 `Dramora`；脚本、后端包名、前端 package 名和 API 路径不因品牌名调整而重命名。

## 当前主功能

### 灵感生成

从故事灵感、人物关系或爽点方向生成短剧剧本。

适合：

- 原创短剧选题；
- 剧情方向验证；
- 人物关系和钩子草案；
- 快速形成可编辑的分集剧本。

### 文本改编

将电影剧本、小说、网文或长文本改编成短剧节奏。

适合：

- 电影剧本改短剧；
- 长剧本短剧化；
- 小说 / 网文改短剧；
- 已有文本整理为可继续创作的结构化素材。

## 当前真实进度

当前 Dramora 已形成“三入口短剧剧本生成与改编工作台”的第一版闭环：

- `idea`：灵感生成短剧剧本；
- `film_script`：电影剧本改编短剧本；
- `novel`：小说 / 网文改编短剧本；
- DeepSeek 三入口真实 LLM 小样本验收已完成；
- `film_script` 的 `target_episode_count` 不一致问题已通过 prompt update 和后端 contract guardrail 修复；
- 生成结果统一为 `ShortDramaScriptOutput`；
- 前端支持在线审看和基础字段编辑；
- TXT / JSON / DOCX 导出已接入后端 Document Export 契约；
- 真实 `.docx` 导入预览已接入前端，支持用户确认后填入或追加到待改编文本；
- `context_options` 已用于 user / workspace / project / session 第一层归属追踪；
- Usage Ledger 第一版 schema / service / 生成链路 metadata 已完成；
- 内部 Auth 第一层已接入：前端登录已调用后端 auth API，当前仍为安全虚构账号和开发期 in-memory auth，不是正式生产权限系统；
- 前端 App 第一轮结构治理已完成，`App.tsx` 已从 2167 行降到 1465 行；
- 已抽出 Toast / Auth / Workspace Navigation / Legacy Idea / Storyboard / Image Prompt / Image Generation hooks；
- `.gitignore` 已强化，避免 `.env`、`.venv`、`node_modules`、`dist`、测试报告、上传文件和本地存储进入公开仓库。

当前仍处于内部开发与部署前准备阶段。项目尚未进入服务器部署、生产上线、正式多人权限系统或真实用量账单阶段。
前端结构治理不代表前端已经彻底完美，但已经降低后续维护风险。

## 当前前端信息架构

```text
登录
  -> 剧本创作
      -> 灵感生成
      -> 文本改编
          -> 电影剧本改编
          -> 小说 / 网文改编
  -> 剧本改编
      -> 长文本整理与短剧化改编
```

分镜、Prompt、图片生成、Asset、Task 等能力作为后续第二大工作流继续保留在工程中，但当前暂缓，不作为当前老板演示和市场试用主界面的重点。

## 当前已具备的工程基础

- FastAPI 后端；
- Pydantic 数据协议；
- React + Vite + TypeScript 前端；
- AppShell / Sidebar / Toast 工作台基础；
- 灵感生成剧本基础链路；
- 文本整理 / 剧本改编 workspace；
- 真实 `.docx` Word 导入预览与用户确认交互；
- 字数限制与后端输入校验；
- 前端接口错误友好提示；
- Document Import / Export Schema、service、endpoint；
- DOCX 导出 service 与文件下载 endpoint；
- 三入口短剧剧本生成与改编 Schema / prompt / service / endpoint；
- ContextOptions 上下文归属基础；
- Usage Ledger 第一版数据契约与非持久化记录；
- 前端 App 第一轮结构治理；
- Playwright e2e 基础验收。

## 技术架构

后端：

- Python；
- FastAPI；
- Pydantic；
- `schemas` / `services` / `routers` 分层；
- Prompt 文件版本化；
- OpenAI-compatible `LLMClient`；
- mock / llm generation mode；
- pytest 测试。

前端：

- React；
- Vite；
- TypeScript；
- AppShell；
- Sidebar；
- 剧本创作首页；
- 剧本改编 workspace；
- 中文 UI；
- 登录后可操作、未登录可浏览的演示门禁。

## 本地快速启动

路径请根据本地 clone 位置调整。

后端启动：

```bash
cd /path/to/Dramora
bash scripts/dev_api.sh
```

前端启动：

```bash
cd /path/to/Dramora/apps/web
npm run dev
```

后端测试：

```bash
cd /path/to/Dramora
python -m pytest tests/api
```

前端构建：

```bash
cd /path/to/Dramora/apps/web
npm run build
```

不要把 `.env`、API Key、真实客户剧本、真实服务器地址或合作敏感资料提交到 Git。

## 项目结构

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

## 文档导航

- [API 合约](docs/API_CONTRACT.md)
- [本地开发](docs/LOCAL_DEV.md)
- [路线图](docs/MVP_ROADMAP.md)
- [项目结构重整计划](docs/PROJECT_STRUCTURE_REFACTOR_PLAN.md)
- [公开仓库与合作边界](docs/COOPERATION_TECH_ASSET_BOUNDARY_DRAFT.md)

## 公开仓库边界与权利声明

当前公开仓库仅用于：

- 技术评审；
- 项目展示；
- 合作沟通。

当前暂未授予开源许可证。公开可见不等于开源授权。未经书面许可，不得商业使用、再分发、转授权或生产部署。

公开仓库不包含：

- 真实 API Key；
- `.env`；
- 真实客户剧本；
- 真实员工数据；
- 真实服务器地址；
- 私有 workflow；
- 模型权重；
- 生产数据库；
- 合作敏感资料。
