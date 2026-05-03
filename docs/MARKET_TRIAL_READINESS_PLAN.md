# Market Trial Readiness Plan｜市场试用准备方案

## 1. 文档目的

本文档用于定义 ManJuFlow 第五阶段后，如何从工程 MVP 进入老板演示、小范围编剧行业试用和合作方评估。

当前目标不是完整文生图 / 文生视频，也不是直接承诺生产级 SaaS。当前目标是先把 ManJuFlow 打造成面向编剧行业的 AI 文字内容创作工作台，让老板、编剧团队、短剧策划、漫剧内容团队和 AI 内容运营人员可以通过网页产品理解、试用和评估核心价值。

本阶段重点：

- 老板可看；
- 小范围用户可试用；
- 合作方技术员可评估；
- 文字内容链路稳定；
- 上传、Assistant、上下文隔离和用量审计边界清晰；
- 不直接进入真实文生图 / 文生视频 / GPU 生产链路。

## 2. 当前市场试用定位

ManJuFlow 当前市场试用版定位为：

```text
面向编剧行业的 AI 文字内容创作与提示词工作台
```

核心能力：

- 灵感生成结构化剧本；
- 已有剧本切分；
- 剧本生成分镜；
- 分镜生成绘图 / 媒体提示词；
- 上传剧本文本的 mock 链路；
- 右侧 AI Assistant 未来辅助改写、扩写、增强钩子、拆分、生成提示词；
- 结果复制 / 导出；
- 工作区隔离设计；
- 公开仓库安全边界。

市场试用版应围绕“文字内容创作效率”和“结构化交付能力”展开，而不是围绕真实图片生成或真实视频生成能力展开。

## 3. 老板演示版完成标准

老板演示版必须满足：

- 网页能正常打开；
- 后端能启动；
- 前端能启动；
- 灵感 → 剧本 → 分镜 → Prompt 链路可演示；
- 已有剧本 → 切分 → 分镜 → Prompt 链路可演示；
- 上传 mock 剧本文档 → `extracted_text` → 切分链路可演示；
- 结果可以复制 / 导出；
- README 能让老板和技术员理解项目价值；
- 演示过程不依赖真实客户数据；
- 不展示真实 API Key；
- 不展示本机绝对路径；
- 不展示真实服务器信息。

老板演示版的重点是“能看懂、能跑通、能体现产品方向”。不要为了演示效果临时接入未经隔离的真实客户数据或真实生产配置。

## 4. 市场试用版完成标准

小范围市场试用版必须满足：

- 后端全量测试通过；
- 前端 `npm run build` 通过；
- 浏览器主流程验收通过；
- 核心链路稳定；
- 上传文件行为有明确边界；
- 聊天记录是否保存有明确策略；
- 工作区 / 项目上下文不串；
- Assistant 至少有 mock UI 和 suggested actions；
- 如果接 DeepSeek Assistant LLM，必须与剧本生成 / Prompt 生成链路隔离；
- 有 `LOCAL_DEV`、`API_CONTRACT`、`MVP_ROADMAP`、`PHASE_5_SUMMARY`；
- 有老板演示脚本；
- 有市场试用说明；
- 有公开仓库与私有部署边界说明。

市场试用版不要求一次性完成企业权限系统、生产级数据合规和真实多租户架构，但必须对这些能力的边界、风险和后续路线说清楚。

## 5. 暂不承诺事项

当前市场试用版暂不承诺：

- 不承诺生产级 SaaS；
- 不承诺多租户正式权限系统；
- 不承诺真实文生图 / 文生视频；
- 不承诺自动成片；
- 不承诺高并发；
- 不承诺长期文件存储；
- 不承诺客户数据生产级合规；
- 不承诺计费系统；
- 不承诺正式商业部署；
- 不承诺真实 ComfyUI / GPU 公共服务。

对外沟通时，应明确 ManJuFlow 当前是市场试用准备阶段，而不是成熟生产平台。

## 6. 用户上传文件策略

市场试用前必须明确以下问题：

- 用户上传的文件保存在哪里；
- 是否保存原文件；
- 是否只保存 `extracted_text`；
- 保存多久；
- 是否允许删除；
- 是否进入 Git；
- 是否进入公开仓库；
- 是否能被其他工作区读取。

建议第一版策略：

- mock 阶段只做 metadata-only upload；
- 真实上传第一版保存到本地受控目录，例如 `storage/uploads` 或 `data/uploads`；
- 上传文件目录必须被 `.gitignore` 排除；
- 公开仓库只提交目录说明和安全样例，不提交真实上传文件；
- 后续用 SQLite 记录 metadata；
- 市场试用前必须明确清理策略和隐私提示；
- 前端不直接读取后端本地路径，只通过 `source_id`、`extracted_text` 和 metadata 工作。

## 7. AI Assistant 策略

用户与 AI 聊天肯定会介入大模型，但 Assistant 必须独立于现有创作链路。

建议策略：

- Assistant 单独 service；
- Assistant 单独 schema；
- Assistant 单独 prompt；
- Assistant 单独 endpoint；
- Assistant 单独 mode：`ASSISTANT_GENERATION_MODE=mock / llm`；
- Assistant 单独 provider 配置：`ASSISTANT_LLM_PROVIDER`；
- Assistant 单独模型配置：`ASSISTANT_LLM_MODEL`；
- Assistant 单独 API Key 环境变量：`ASSISTANT_API_KEY` 或 `ASSISTANT_LLM_API_KEY`；
- 可以使用 DeepSeek，但不要和剧本生成、分镜生成、Prompt 生成逻辑混在一起；
- Assistant 不应自动修改生产数据，suggested actions 需要用户确认。

底层可以复用通用 LLM HTTP 能力，但业务配置、prompt、上下文和用量记录必须隔离。

## 8. 聊天记录保存策略

市场试用前必须明确：

- 是否保存聊天记录；
- 保存在哪里；
- 是否按 `workspace_id` / `project_id` / `session_id` 隔离；
- 是否可以清空；
- 是否可以导出；
- 是否进入训练；
- 是否进入公开仓库。

建议第一版策略：

- mock 阶段前端 state / localStorage 即可；
- 后续试用版可以用 SQLite 保存 conversation 和 messages；
- 必须绑定 `workspace_id` / `project_id` / `session_id`；
- 不保存真实敏感数据到公开仓库；
- 后续需要隐私说明和清理策略；
- Assistant suggested actions 的应用结果也应可回溯。

## 9. 工作区与上下文隔离

市场试用时必须避免：

- A 项目的剧本被带入 B 项目；
- A 用户聊天内容影响 B 用户；
- Assistant 引用错误项目上下文；
- Prompt 生成串用上一轮数据。

建议验收标准：

- 所有核心请求后续都应携带 `workspace_id` / `project_id` / `session_id`；
- `AssistantContext` 必须显式传入；
- 不让模型从全局状态里隐式读取项目内容；
- 前端切换 workspace 时清楚展示当前上下文；
- 后续测试要覆盖上下文隔离；
- 跨项目引用必须显式确认；
- suggested actions 默认只作用于当前项目和当前 workspace。

## 10. 市场试用前剩余工作清单

建议剩余小闭环：

- README / `LOCAL_DEV` / `API_CONTRACT` 对齐；
- `MARKET_TRIAL_READINESS_PLAN`；
- `BOSS_DEMO_SCRIPT`；
- 已有剧本切分结果一键带入绘图 Prompt；
- 浏览器验收 Existing Script → Segmentation → Storyboard → Prompt；
- `AI_ASSISTANT_PANEL_DESIGN`；
- Assistant Schema；
- Assistant mock service；
- Assistant endpoint；
- Assistant 前端 UI；
- Assistant suggested actions；
- Assistant DeepSeek 独立配置；
- 上传文件真实 multipart 第一版；
- 上传文件 storage / `.gitignore`；
- 聊天记录策略；
- mock auth / workspace isolation；
- 前端 UI 信息架构整理；
- 全量测试；
- `PHASE_5_SUMMARY`；
- `MARKET_TRIAL_SUMMARY`。

以上任务应继续按“小闭环、可测试、可回滚”的方式推进，不建议一次性大重构。

## 11. 验收命令

市场试用前必须通过以下命令。

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

Git 状态：

```bash
cd /path/to/ManJuFlow
git status
```

浏览器验收：

- 打开前端；
- 测试灵感链路；
- 测试已有剧本链路；
- 测试上传 mock；
- 测试 Assistant；
- 测试复制 / 导出。

## 12. 风险与缓解策略

### 用户数据泄露风险

风险：试用用户可能上传真实剧本、个人信息或合作方资料。

缓解：

- 试用前明确隐私提示；
- mock 阶段不接真实客户数据；
- 真实上传目录不进入 Git；
- 日志不打印完整剧本内容；
- 提供清理和删除策略。

### 上传文件误提交风险

风险：上传文件、提取文本或 metadata 被误提交到公开仓库。

缓解：

- `storage/` 或 `data/uploads/` 必须进入 `.gitignore`；
- Git 提交前检查 `git status`；
- 公开仓库只保留虚构样例；
- 真实文件留在本地或私有部署环境。

### 聊天上下文串项目风险

风险：Assistant 把 A 项目的上下文用于 B 项目。

缓解：

- 每次请求携带 `project_id` / `workspace_id` / `session_id`；
- AssistantContext 显式传入；
- suggested actions 带目标 workspace；
- 跨项目引用必须确认。

### DeepSeek Assistant 与创作链路混用风险

风险：Assistant Chat 与剧本生成、分镜生成、Prompt 生成共用配置和 prompt，导致调用边界混乱。

缓解：

- Assistant 单独 schema / service / prompt / endpoint；
- Assistant 单独 provider 和模型配置；
- Assistant 单独 API Key 环境变量；
- UsageLedger 中区分 feature_name 和 operation_type。

### API Key 泄露风险

风险：真实 API Key 被写入文档、代码、截图或日志。

缓解：

- 真实 key 只进入私有 `.env`；
- `.env` 不提交；
- 日志脱敏；
- 公开文档只写变量名，不写真实值；
- 发布截图前检查敏感信息。

### 老板误以为已经是生产级 SaaS 的预期管理风险

风险：演示效果较完整，导致误判为可直接商用生产系统。

缓解：

- README 和演示脚本明确 active MVP development；
- 明确暂不承诺事项；
- 区分老板演示版、市场试用版和生产部署版；
- 不把 mock 能力描述成真实生产能力。

### 试用用户上传真实剧本的版权 / 权属风险

风险：试用素材版权不清晰，后续引发争议。

缓解：

- 试用前要求使用自有或授权素材；
- 提供虚构样例；
- 不把试用素材提交公开仓库；
- 后续补充用户协议和数据处理说明。

### 结果质量不稳定风险

风险：AI 输出不稳定，影响编剧团队信任。

缓解：

- 保留 mock 和可控样例；
- 输出结果必须可编辑、可复制、可导出；
- 关键链路支持重试；
- 后续增加版本记录和人工确认流程；
- 对外说明 AI 输出为辅助，不等于最终定稿。

## 13. 第 168 步验收标准

- `docs/MARKET_TRIAL_READINESS_PLAN.md` 已新增；
- 文档明确老板演示版标准；
- 文档明确市场试用版标准；
- 文档明确暂不承诺事项；
- 文档明确上传文件策略；
- 文档明确 Assistant 独立 DeepSeek 策略；
- 文档明确聊天记录保存策略；
- 文档明确 workspace / project / session 隔离；
- 文档明确剩余工作清单；
- 不修改代码；
- 不包含敏感信息。
