# Dramora｜剧作工坊

[中文](README.zh-CN.md) | [English](README.en.md)

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)
![Schema](https://img.shields.io/badge/Schema-Pydantic-e92063)
![Mode](https://img.shields.io/badge/Mode-Mock--first-0f766e)

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

分镜、Prompt、图片生成、Asset、Task 等能力作为后续工作流继续保留在工程中，但不作为当前老板演示和市场试用主界面的重点。

## 当前已具备的工程基础

- FastAPI 后端；
- Pydantic 数据协议；
- React + Vite + TypeScript 前端；
- AppShell / Sidebar / Toast 工作台基础；
- 灵感生成剧本基础链路；
- 文本整理 / 剧本改编 workspace；
- Word 剧本文档模拟上传；
- 字数限制与后端输入校验；
- 前端接口错误友好提示；
- Document Export Schema；
- 三入口短剧剧本生成与改编 Schema / registry / mock service / endpoint 基础；
- mock-first 与本地演示优先策略。

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
