# ManJuFlow｜漫剧流

[中文](README.zh-CN.md) | [English](README.en.md)

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)
![Schema](https://img.shields.io/badge/Schema-Pydantic-e92063)
![Mode](https://img.shields.io/badge/Mode-Mock--first-0f766e)

## Hero

**ManJuFlow｜漫剧流** 当前正在重整为一个面向编剧、短剧策划、漫剧内容团队的 AI 短剧剧本生成与改编工作台。

用户先登录内部账户，再选择三种创作方式之一：灵感生成短剧剧本、电影剧本改编短剧剧本、小说改编短剧剧本。生成后可在线编辑、下载 / 导出、上传修改稿，并在后续进入短剧剧本切分 / 分镜 / Prompt。

当前阶段：**Active MVP Development｜Phase 5 Three-entry Short-drama Script Workbench**

## 项目定位

ManJuFlow 当前主产品定位是 AI 短剧剧本生成与改编工作台，用于把灵感、电影剧本片段或小说文本逐步转化为可编辑、可导出、可继续进入后续工作流的短剧剧本。

当前项目重点不是直接“自动成片”，也不是优先推进文生图 / 文生视频，而是先把短剧剧本生成、改编、在线编辑、下载导出、上传修改稿和 Assistant 辅助工作流打稳。它面向短剧、漫剧和文字内容生产场景，重点服务非技术内容团队，让编剧、短剧策划、漫剧内容团队和运营人员可以通过网页工作台完成可追踪、可评审、可交接的短剧剧本生产链路。

当前公开仓库用于技术评审、项目展示和合作沟通。真实客户数据、真实账号、真实 ComfyUI / GPU 配置、私有 workflow 和模型权重应留在私有部署环境。

## 当前已完成能力

### Phase 1｜Idea → Script

- 灵感输入；
- 结构化短剧剧本输出；
- `POST /api/scripts/generate`；
- 前端展示、复制、导出；
- mock / llm 模式。

### Phase 2｜Script → Storyboard

- 剧本转导演分镜；
- `StoryboardOutput`；
- `POST /api/storyboards/generate`；
- 前端分镜展示；
- 剧本结果带入分镜；
- 分镜 JSON 复制 / 导出。

### Phase 3｜Storyboard → ImagePrompt

- 分镜转 AI 绘图 Prompt；
- `ImagePromptInput` / `ImagePromptOutput`；
- `POST /api/prompts/generate`；
- 多文本 LLM provider；
- Prompt 中文 / 英文输出；
- 前端展示、复制、导出。

### Phase 4｜ImagePrompt → ImageGeneration Mock / Bundle

- ImageGeneration mock；
- `ImageGenerationBundleOutput`；
- Asset / RenderTask mock；
- `POST /api/images/generate`；
- `POST /api/images/generate-bundle`；
- AppShell / Sidebar / Toast；
- ComfyUI / 远端 GPU 私有部署文档。

### Phase 5｜Three-entry Short-drama Script Workbench

- 已有剧本切分 Schema / Service / Endpoint；
- 前端“已有剧本”工作区；
- Mock Word 剧本文档上传；
- `extracted_text` 自动填入切分区；
- 切分结果带入分镜；
- Workspace Context Isolation 设计；
- 上传 / Auth / UsageLedger 设计；
- 前端中文化规范；
- README 双语升级规划。

### Phase 5 Update｜Three-entry Short-drama Script Workbench

当前第五阶段产品主线已调整为三入口短剧剧本生成与改编工作台：

- 灵感生成短剧剧本：已具备基础 Idea → Script 能力，继续强化短剧集数、钩子和分集结构；
- 电影剧本改编短剧剧本：规划中，下一步按 mock 优先、独立 prompt、独立 source_mode 推进；
- 小说改编短剧剧本：规划中，下一步按 mock 优先、独立 prompt、独立 source_mode 推进。

切分 / 分镜 / Prompt 仍然保留，但调整为生成短剧剧本后的下一大功能预备，不再作为当前首页主入口。Image Generation / Video Generation 暂不作为市场试用重点。

## 当前产品主入口

未来工作台入口规划：

1. 内部账号 / mock login；
2. 进入三入口选择页；
3. 选择创作方式：
   - 灵感生成短剧剧本；
   - 电影剧本改编短剧剧本；
   - 小说改编短剧剧本；
4. 进入对应生成 / 改编页面；
5. 在线编辑短剧剧本；
6. 下载 DOCX / TXT / JSON 或上传修改稿；
7. 后续可继续进入短剧剧本切分 / 分镜 / Prompt。

## AI Assistant 定位

AI Assistant 不是普通聊天框，而是编剧助手 / 改编助手 / 工作流助手。

它未来将辅助：

- 改写灵感；
- 提炼电影剧本改编策略；
- 梳理小说人物关系；
- 增强短剧钩子；
- 将当前结果带入下一步；
- 通过 suggested actions 执行操作，并由用户确认。

Assistant 必须独立于三入口主生成链路，拥有独立 schema / service / endpoint / prompt / env 配置。

## 工作流概览

```mermaid
flowchart LR
  Login[内部账号 / Mock Login] --> Entry[三入口选择]
  Entry --> Idea[灵感生成短剧]
  Entry --> Film[电影剧本改短剧]
  Entry --> Novel[小说改短剧]
  Idea --> Script[短剧剧本]
  Film --> Script
  Novel --> Script
  Script --> Edit[在线编辑 / 导出 / 上传修改稿]
  Edit --> Next[下一大功能：切分 / 分镜 / Prompt]
```

## 技术架构

后端：

- Python；
- FastAPI；
- Pydantic；
- `schemas` / `services` / `routers` 分层；
- Prompt 文件版本化；
- OpenAI-compatible `LLMClient`；
- mock / llm generation mode；
- provider 配置边界；
- pytest 测试。

前端：

- React；
- Vite；
- TypeScript；
- AppShell；
- Sidebar；
- Workspace UI；
- Toast；
- `ScriptSegmentationWorkspace`；
- 中文 UI；
- Prompt 中文 / 英文输出。

工程原则：

- 模块化优先；
- 数据协议优先；
- mock-first；
- 先本地跑通；
- 每个小闭环可测试；
- 不过早引入复杂基础设施；
- 公开仓库安全边界优先。

## 本地快速启动

路径请根据本地 clone 位置调整。

后端启动：

```bash
cd /path/to/ManJuFlow
bash scripts/dev_api.sh
```

清理端口并重启后端：

```bash
cd /path/to/ManJuFlow
bash scripts/kill_api_port.sh
bash scripts/dev_api.sh
```

前端启动：

```bash
cd /path/to/ManJuFlow/apps/web
npm run dev
```

后端测试：

```bash
cd /path/to/ManJuFlow
python -m pytest tests/api
```

前端构建：

```bash
cd /path/to/ManJuFlow/apps/web
npm run build
```

不要把 `.env`、API Key、真实客户数据提交到 Git。

## 项目结构

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
│           │   ├── layout/
│           │   └── workspaces/
│           └── App.tsx
├── docs/
├── examples/
├── scripts/
├── tests/
└── README.md
```

- `apps/api`：FastAPI 后端；
- `apps/web`：React + Vite 前端；
- `docs`：阶段文档、设计文档、runbook、安全边界；
- `tests/api`：后端测试；
- `scripts`：本地开发脚本；
- `examples`：安全示例。

## API 概览

- `GET /health`
- `GET /api/system/status`
- `POST /api/scripts/generate`
- `POST /api/scripts/segment`
- `POST /api/storyboards/generate`
- `POST /api/prompts/generate`
- `POST /api/images/generate`
- `POST /api/images/generate-bundle`
- `POST /api/uploads/script`

说明：

- `/api/uploads/script` 当前是 JSON mock metadata-only upload，不是真实 multipart 文件上传；
- `/api/images/generate` 和 `/api/images/generate-bundle` 当前是 mock，不接真实 ComfyUI / GPU。

## 安全边界与 Usage Notice

当前公开仓库仅用于：

- 技术评审；
- 项目展示；
- 合作沟通。

重要说明：

- Public visibility does not imply open-source authorization；
- 当前仓库暂未授予开源许可证；
- 未经书面许可，不得商业使用、再分发、转授权或生产部署；
- 真实 API Key、`.env`、客户数据、员工数据、真实服务器信息、私有 workflow、模型权重不进入公开仓库；
- 真实 ComfyUI / GPU / workflow / 客户资产应放在私有部署环境。

公开仓库可以包含：

- Schema；
- mock service；
- mock endpoint；
- provider interface；
- placeholder；
- 文档和 runbook；
- 安全的虚构样例；
- 本地 demo。

公开仓库不能包含：

- API Key；
- `.env`；
- SSH Key；
- 真实客户剧本；
- 真实员工信息；
- 真实服务器地址；
- 私有 ComfyUI workflow；
- 模型权重；
- 生产输出资产；
- 合作方敏感信息。

## Roadmap

后续方向：

- 三入口 Schema / Prompt / source_mode 注册；
- 电影剧本改短剧 mock / llm；
- 小说改短剧 mock / llm；
- 前端三入口选择页；
- 真实 `.docx` 文件上传与文本解析；
- 在线编辑与 DOCX 下载；
- Mock Internal Auth；
- Assistant 作为编剧助手 / 改编助手 / 工作流助手；
- Assistant suggested actions；
- UsageLedger 用量与人民币成本估算；
- 短剧剧本切分 / 分镜 / Prompt 作为下一大功能；
- README 后续维护与文档同步；
- 私有 ComfyUI 小样本联调；
- Asset Manager / Task Center 深化；
- Workspace / Project Context Isolation 落地；
- 私有部署与权限系统。

## 文档导航

- [API Contract](docs/API_CONTRACT.md)
- [Local Dev](docs/LOCAL_DEV.md)
- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [Project Structure Refactor Plan](docs/PROJECT_STRUCTURE_REFACTOR_PLAN.md)
- [Frontend Localization and Prompt Language Guide](docs/FRONTEND_LOCALIZATION_AND_PROMPT_LANGUAGE_GUIDE.md)
- [Cooperation Tech Asset Boundary Draft](docs/COOPERATION_TECH_ASSET_BOUNDARY_DRAFT.md)
- [README Bilingual Upgrade Plan](docs/README_BILINGUAL_UPGRADE_PLAN.md)
- [Phase 3 Summary](docs/PHASE_3_SUMMARY.md)
- [Phase 4 Summary](docs/PHASE_4_SUMMARY.md)
- [Phase 5 Text-to-Prompt Workbench Plan](docs/PHASE_5_TEXT_TO_PROMPT_WORKBENCH_PLAN.md)

## 当前状态说明

ManJuFlow 仍处于 active MVP development。

当前公开仓库展示的是可评审、可运行、可迁移的工程主干和 mock-first 闭环。真实生产部署、真实账号、真实客户数据、真实 GPU / ComfyUI、真实 workflow 需要进入私有环境单独配置。
