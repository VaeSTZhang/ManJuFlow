# Project Structure and Configuration Audit｜项目结构与配置源审计

## 1. 审计目标

本次审计用于保证 Dramora｜剧作工坊 后续由技术组接手时结构清晰、配置单一、安全边界明确。

重点检查：

- 根目录文件是否清爽；
- 真实本地配置是否只来自项目根目录 `.env`；
- `.env.example` 是否只作为公开模板；
- LLM provider 配置是否避免 DeepSeek 写死；
- docs 是否需要后续分层；
- 前端和后端结构是否适合继续产品化。

本次审计只做记录和建议，不移动历史文档，不重构代码，不读取或输出真实 `.env` 内容。

## 2. 当前仓库结构概览

当前根目录主要结构：

- `apps/api`：FastAPI 后端；
- `apps/web`：React + Vite 前端；
- `docs`：阶段文档、设计文档、运行说明、安全边界；
- `examples`：安全示例；
- `scripts`：本地开发脚本；
- `tests`：后端测试；
- `.env.example`：公开配置模板；
- `.gitignore`：忽略本地环境、构建产物和运行时输出；
- `README.md` / `README.zh-CN.md` / `README.en.md`：GitHub 默认中文主页、中文完整说明、英文说明。

本地检查到项目根目录存在 `.env`，但没有读取内容。`git ls-files` 结果显示当前只有 `.env.example` 被 Git 跟踪，`.env` 未被跟踪。

## 3. 配置源原则

后续配置源应保持单一：

- 真实本地配置只放项目根目录 `.env`；
- `.env` 不提交；
- `.env.example` 是唯一公开模板；
- 不再维护 `apps/api/.env`；
- 不在 README / docs / code 中写真实 API Key；
- DeepSeek 是默认推荐 provider，但不写死；
- Mimo / Kimi / MiniMax 等 provider 通过统一 LLM config 扩展；
- 业务 service 不直接硬编码具体模型。

当前代码层检查：

- `apps/api/app/config.py` 使用 `PROJECT_ROOT / ".env"`；
- `apps/api/.env` 当前不存在；
- `docs/LOCAL_DEV.md` 和 `docs/LLM_SETUP.md` 已说明真实配置统一放项目根目录 `.env`，不再需要 `apps/api/.env`；
- `.env.example` 中 DeepSeek / Mimo / Kimi / MiniMax 均为公开占位字段，没有真实 Key。
- 第 219 步已补齐 `DEFAULT_LLM_PROVIDER`、`DEFAULT_SCRIPT_MODEL`、`LLM_REQUEST_TIMEOUT_SECONDS`、`ASSISTANT_GENERATION_MODE`，并保留 `LLM_PROVIDER` / `LLM_MODEL` 兼容字段。

## 4. LLM 配置建议

第 219 步已开始统一字段命名，并以 `.env.example` 和 `apps/api/app/config.py` 为准。

建议字段：

- `DEFAULT_LLM_PROVIDER`
- `DEFAULT_SCRIPT_MODEL`
- `DEEPSEEK_API_KEY`
- `MIMO_API_KEY`
- `KIMI_API_KEY`
- `MINIMAX_API_KEY`
- `LLM_REQUEST_TIMEOUT_SECONDS`
- `SCRIPT_GENERATION_MODE`
- `IMAGE_PROMPT_GENERATION_MODE`
- `ASSISTANT_GENERATION_MODE`

保留兼容字段包括：

- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `LLM_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `DEEPSEEK_API_KEY`
- `MIMO_BASE_URL`
- `MIMO_MODEL`
- `MIMO_API_KEY`
- `KIMI_BASE_URL`
- `KIMI_MODEL`
- `KIMI_API_KEY`
- `MINIMAX_BASE_URL`
- `MINIMAX_MODEL`
- `MINIMAX_API_KEY`
- `SCRIPT_GENERATION_MODE`
- `STORYBOARD_GENERATION_MODE`
- `IMAGE_PROMPT_GENERATION_MODE`

当前状态：

- `DEFAULT_LLM_PROVIDER` 和 `DEFAULT_SCRIPT_MODEL` 已作为 Dramora 推荐默认配置入口；
- `LLM_PROVIDER` / `LLM_MODEL` 继续保留，避免破坏当前 LLMClient 兼容路径；
- `LLM_REQUEST_TIMEOUT_SECONDS` 与 `ASSISTANT_GENERATION_MODE` 已进入配置模板和 `config.py`；
- 请求级 provider / model 已进入统一 `AIRequestOptions`，不要求用户每次修改 `.env` 才能切换前端创作模型；
- 后续真实 LLM 接入时，应继续避免在业务 service 中硬编码 DeepSeek。

## 5. 公开仓库安全边界

以下内容不能进入公开仓库：

- `.env`
- API Key
- 真实客户剧本
- 真实员工数据
- 真实上传 Word
- 真实导出 Word
- 真实服务器地址
- 模型权重
- 私有 workflow
- 合作方敏感资料

当前 `.gitignore` 已包含：

- `.env`
- `.env.local`
- `.venv/`
- `node_modules/`
- `dist/`
- `build/`
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `storage/`
- `outputs/`
- `tmp/`
- `temp/`
- `*.tsbuildinfo`

建议后续补充：

- `.env.*`
- `!.env.example`
- `storage/uploads/`
- `storage/exports/`
- `apps/api/storage/uploads/`
- `apps/api/storage/exports/`

当前没有发现 `.env`、`.idea`、`.pytest_cache`、上传文件或构建产物被 Git 跟踪。`git ls-files` 仅显示 `.env.example` 被跟踪。

## 6. docs 分层建议

当前 `docs/` 文件较多，包含阶段总结、产品设计、技术设计、运行说明、安全边界和模型比较资料。数量已经较大，继续平铺会影响技术组接手时的检索效率。

未来建议整理为：

```text
docs/
  product/
  architecture/
  api/
  deployment/
  runbooks/
  phases/
  security/
```

本步不移动历史文档，避免破坏已有链接和造成大 diff。建议等 README、路线图和核心文档稳定后，再做单独的 docs 分层迁移。

## 7. 前端结构建议

当前前端目录方向合理：

- `apps/web/src/components/creation/`：Dramora 剧本创作首页；
- `apps/web/src/components/workspaces/`：剧本改编及历史工作区；
- `apps/web/src/components/layout/`：AppShell / Sidebar / Toast；
- `apps/web/src/api/`：前端 API 封装；
- `apps/web/src/types/`：前端类型；
- `apps/web/src/constants/`：入口 registry 等配置。

后续建议：

- `App.tsx` 不应继续膨胀；
- Dramora 主线应围绕 `CreationHome` / `ScriptCreation` / `ScriptAdaptation`；
- 后续新增 `CreativeModelPanel`，统一 DeepSeek / Mimo / Kimi / MiniMax 模型选择；
- 后续新增 `ShortDramaScriptResult`，统一展示生成或改编后的短剧剧本；
- 后续拆出 `AuthButton` / `AuthShell`；
- 分镜、Prompt、图片生成应作为后续工作流，不在老板演示主界面突出。

## 8. 后端结构建议

当前后端三层方向正确：

- `apps/api/app/schemas`
- `apps/api/app/services`
- `apps/api/app/routers`

已有 `apps/api/app/services/script_generation/` 用于三入口剧本生成方向，是合理演进。

后续新增能力时建议继续按功能拆分：

- `auth`
- `usage`
- `assistant`
- `document`
- `script_generation`
- `script_segmentation`
- `llm provider config`

LLM provider 配置统一走 `config.py` + `LLMClient`。不要在业务 service 里直接写死 provider，也不要让每个业务模块各自维护一套模型配置。

## 9. 立即需要修复的问题

本次审计未发现公开仓库中应立即删除的敏感配置。

需要后续确认或优化：

- `.gitignore` 建议补充 `.env.*` 与 `!.env.example`；
- `.gitignore` 建议显式补充上传 / 导出目录；
- `.env.example` 与 `config.py` 的 LLM 默认字段已在第 219 步部分落地，后续真实 LLM 验收时再确认 LLMClient 使用路径；
- 当前 `docs/` 文件数量较多，后续应单独做分层整理；
- `tests/api/__pycache__` 和 `apps/api/app/__pycache__` 等本地缓存存在，但已被 `.gitignore` 覆盖且未被 Git 跟踪。

## 10. 后续建议步骤

- 第 206 步：更新当前 README 和本地开发文档里的 Dramora 路径说明；
- 第 207 步：统一 `.env.example` 与 `config.py` 的 LLM 配置字段；
- 第 208 步：补充 `LOCAL_DEV` / `LLM_SETUP` 的单一配置源说明；
- 第 209 步：前端 `App.tsx` 拆分计划；
- 第 210 步：`ShortDramaScriptResult` 组件；
- 第 211 步：`CreativeModelPanel` 组件。
