# Dramora｜剧作工坊 MVP Roadmap

## 当前产品主线

Dramora 当前第五阶段主线已调整为：

```text
内部账号 / mock login
→ 三入口选择
→ 灵感生成短剧剧本 / 电影剧本改短剧 / 小说改短剧
→ 在线编辑 / DOCX 下载 / 上传修改稿
→ 用量记录 / 质量评审
→ 下一大功能：短剧剧本切分 / 分镜 / Prompt
```

当前市场试用重点是 **AI 短剧剧本生成与改编工作台**，不是文生图、文生视频或自动成片。

## 已完成基础能力

- Phase 1：Idea → Script；
- Phase 2：Script → Storyboard；
- Phase 3：Storyboard → ImagePrompt；
- Phase 4：ImagePrompt → ImageGeneration mock / bundle / asset / task / workspace；
- Phase 5 已完成部分：
  - Existing Script Segmentation schema / service / endpoint；
  - 前端已有剧本工作区；
  - mock Word upload；
  - 输入长度限制与前端字数提示；
  - 后端统一输入长度校验；
  - Document Round-trip 方案；
  - Document Export Schema；
  - 三入口短剧工作台重整方案；
  - 三入口项目结构重整方案；
  - 市场试用方案和老板演示脚本已按三入口方向更新。

## 当前阶段状态｜Phase 5A

Phase 5A 当前已形成三入口剧本生成与改编工作台的第一版主干：

- 灵感生成短剧剧本；
- 电影剧本改编短剧本；
- 小说 / 网文改编短剧本；
- DeepSeek 三入口真实 LLM 小样本验收已完成；
- `film_script` 的 `target_episode_count` 问题已通过 prompt update 和后端 contract guardrail 修复；
- `ShortDramaScriptOutput` 统一结果展示与在线基础编辑已完成；
- TXT / JSON / DOCX 导出闭环已完成；
- Real Word `.docx` import preview has been implemented and browser-validated；
- Document round-trip first version 已跑通：import preview → user confirmation → script input → generation → edit → DOCX export；
- `ContextOptions` 第一层已接入生成、文档导入和文档导出；
- Usage Ledger 持久化 B 组已完成本地 / 单机内部试运行前基础：SQLite repository + 剧本生成写入 + 文档导入预览写入 + TXT / JSON / DOCX 导出写入 + 脱敏测试；
- Internal Auth 持久化 A 组已完成本地 / 单机内部试运行前基础：SQLite repository + password_hash helper + safe seed user + auth service repository migration + endpoint security regression + frontend login e2e regression；
- Project / Session / Document 归属组已完成后端 ownership records、guardrail 测试和前端最小 project/session context 迁移；
- `context_options` 当前可从 auth response 与前端当前创作会话推导 user / workspace / project / session 归属；
- `.env.example` / environment variables checklist 已完成，公开仓库只保留占位配置；
- Local Data Storage and Backup Plan 已完成，数据库、上传、导出、日志、测试报告和构建产物目录边界已明确；
- Frontend App first-round structure refactor completed；
- `App.tsx` 已从 2167 行降到 1465 行；
- 已抽出 Toast / Auth / Workspace Navigation / Legacy Idea / Storyboard / Image Prompt / Image Generation hooks；
- 前端结构治理不再是服务器部署前最大阻塞项；
- `.gitignore` 已强化，避免 `.env`、`.venv`、`node_modules`、`dist`、测试报告、上传文件和本地存储进入公开仓库；
- 当前自动化回归状态：后端 `tests/api` 557 passed，前端 `npm run build` passed，前端 `npm run test:e2e` 13 passed。

当前仍是内部开发与部署前准备阶段，不代表已生产上线，也不代表正式多人权限系统已完成。
Auth 当前已具备本地 / 单机内部试运行前的持久化基础，但仍保留开发期 `safe_creator` 安全虚构测试账号，不代表正式内部账号已配置。正式内部试运行前需替换真实内部账号，并补齐 token 过期 / 刷新策略、权限中间件和生产级审计。
Project / Session / Document 当前已具备最小归属链路，但仍未实现完整项目管理后台、项目列表 UI、云端文件资产库或复杂 RBAC。
环境变量清单、本地安全 Runbook 和本地数据目录 / 备份方案已完成第一版，但仍未进入云端部署；真实 token 生命周期、权限中间件、服务器 secret 管理、日志脱敏、全量回归、真实 DeepSeek 小样本复测、全链路验收和 Go / No-Go checklist 仍属于后续部署前 / 部署阶段任务。

## P0｜当前优先级

- Three-entry script workbench stabilization；
- Real LLM quality acceptance follow-up；
- ContextOptions and Usage Ledger foundation hardening；
- Document import/export safety and regression checks；
- Real Word `.docx` import preview regression；
- Auth production token strategy, Usage Ledger query page / admin audit / precise billing reconciliation, Deployment Runbook, environment variables, HTTPS/CORS, logging redaction, and permission boundary；
- Deployment preparation runbook, without starting production deployment yet。

中文说明：

- 三入口短剧剧本工作台稳定化；
- 真实模型质量验收复查；
- ContextOptions 与 Usage Ledger 第一层治理；
- Document import/export 安全和回归检查；
- 真实 Word `.docx` 导入预览回归；
- Auth 生产 token 策略、Usage Ledger 查询页面 / 管理员审计 / 精确账单对账、部署 Runbook、环境变量、HTTPS/CORS、日志脱敏和权限边界；
- 部署前 Runbook，不立即推进生产部署。

## P1｜下一阶段能力

- Internal account SQLite auth hardening；
- Usage Ledger query page and admin audit view；
- Deployment Runbook and environment variable checklist；
- HTTPS / CORS / logging redaction / permission boundary hardening；
- Production upload storage；
- Auth-bound project storage；
- Quality review；
- Script segmentation / storyboard / prompt as next big feature；
- Deployment safety runbook。

中文说明：

- 内部账号：SQLite auth 基础已完成，继续补齐真实内部账号、token 生命周期和权限边界；
- Usage Ledger 持久化设计：记录内部试用中的模型调用和成本线索；
- 部署 Runbook 与环境变量清单；
- HTTPS / CORS / 日志脱敏 / 权限边界加固；
- 生产上传文件存储；
- 账号 / 项目绑定后的文档存储；
- 质量评审：评估生成剧本的可用性、短剧节奏和改编质量；
- 短剧剧本切分 / 分镜 / Prompt 作为下一大功能；
- 部署前安全 Runbook。

Auth 后续仍需完成：

- 真实内部账号替换开发期 `safe_creator`；
- 角色权限校验；
- 生产 token 策略；
- 登录审计与管理员账号管理。

## P2｜后续媒体生成方向

- Image generation；
- Video generation；
- ComfyUI / GPU deployment。

中文说明：

- 图片生成；
- 视频生成；
- ComfyUI / GPU 私有部署。

这些能力不作为当前市场试用第一重点。进入真实 ComfyUI / GPU 前，必须继续遵守私有部署 checklist 和公开仓库安全边界。

## 当前暂不做

- 真实文生图作为市场试用主功能；
- 文生视频；
- 自动成片；
- 真实 ComfyUI 公共服务；
- 真实 GPU 服务器接入；
- 复杂多租户正式权限系统；
- 高并发 SaaS；
- Redis / Celery / MinIO；
- 复杂多 Agent；
- 右侧 AI 聊天界面 / AI Assistant；
- AssistantPanel、`/api/assistant/chat`、`suggested_actions`；
- Docker 生产部署。
- 服务器 / 域名 / HTTPS 立即上线。

说明：这里取消的是右侧聊天式 AI Assistant，不是取消 Dramora 的核心 LLM 创作能力。Dramora 仍继续通过 DeepSeek / Mimo / Kimi / MiniMax 等模型进行剧本生成、电影剧本改编、小说 / 网文改编、扩写、质量评审和后续分镜 / Prompt 生成。

## 项目推进原则

- 每次只做一个小闭环；
- 不为了赶进度写死结构；
- 三入口通过 `source_mode`、独立 prompt、独立 form、独立 service 边界推进；
- Document import/export 独立于 upload mock；
- 当前版本不规划右侧聊天式 AI Assistant；历史方案仅归档，不进入当前实施路线；
- AI 改写、扩写和质量评审应作为剧本编辑区、质量评审区或局部操作能力接入，而不是作为通用聊天窗口接入；
- 公开仓库不提交 API Key、`.env`、真实客户数据、真实服务器地址、私有 workflow 或模型权重；
- 每个阶段完成后测试、文档、再提交。
