# Phase 5A Productization Execution Plan｜第五阶段 A：产品化执行蓝图

> 当前状态：老板已取消当前版本的右侧 AI 聊天界面、AI Assistant、`/api/assistant/chat` 和 `suggested_actions`。本文已按当前路线调整：Phase 5A 聚焦三入口短剧剧本生成 / 改编、在线编辑、Word / TXT / JSON 导入导出、创作模型选择、用量记录、质量评审和内部试用质量加固。历史 Assistant 方案不再作为当前版本能力或服务器购买前置事项。

## 1. 文档目的

本文档是 Phase 5A 后续开发的总控执行蓝图，用于统一产品定位、工程结构、功能边界、开发顺序和验收标准。

需要明确：

- ManJuFlow 已经不是一个简单小 demo；
- 当前目标是产品级 AI 短剧剧本生成与改编工作台；
- 不追求一步到位；
- 不为了赶进度写死结构；
- 所有功能按小闭环交付；
- 每一步必须可测试、可回滚、可评审。

本文件用于后续继续开发时校准方向，避免需求变化导致代码散乱、文档冲突和架构返工。

## 2. 当前产品主定位

ManJuFlow 当前阶段是面向编剧、短剧策划、漫剧内容团队的 AI 短剧剧本生成与改编工作台。

当前主线不是：

- 文生图；
- 文生视频；
- 自动成片；
- 普通聊天机器人。

核心价值：

- 提升短剧剧本生成效率；
- 支持多来源改编；
- 支持在线编辑和文档往返；
- 支持创作模型选择、质量评审和用量记录；
- 为后续 Prompt / 分镜 / 媒体生成打基础。

当前主入口：

1. 灵感生成短剧剧本；
2. 电影剧本改编短剧剧本；
3. 小说改编短剧剧本。

## 3. Phase 5A 与 Phase 5B 边界

### Phase 5A

Phase 5A 聚焦短剧剧本生成与改编工作台：

- 登录 / mock login；
- 三入口选择；
- 灵感生成短剧；
- 电影剧本改短剧；
- 小说改短剧；
- 在线编辑；
- DOCX 下载；
- 上传修改稿；
- 用量记录；
- 质量评审；
- 结果保存策略。

### Phase 5B

Phase 5B 聚焦短剧剧本生成之后的下一大功能：

- 短剧剧本切分；
- 分镜；
- Prompt；
- Prompt 页面返回箭头；
- Prompt 页面状态保留；
- 后续媒体生成预备。

说明：

- Phase 5B 不是废弃；
- Phase 5B 是在 Phase 5A 之后推进的下一大功能；
- 当前市场试用优先级应先保证 Phase 5A 体验清晰、可用、可演示。

## 4. 当前已完成基础

当前已完成的工程基础包括：

- Idea → Script；
- Script → Storyboard；
- Storyboard → ImagePrompt；
- ImageGeneration mock；
- Existing Script Segmentation；
- Upload mock；
- Input limits；
- Backend input validation；
- Frontend backend error detail；
- Document Export Schema；
- 三入口重整文档；
- 项目结构重整文档；
- 三入口到 Prompt 导航设计；
- README / Roadmap / Boss Demo / Market Trial 已同步三入口方向。

这些能力不会废弃，但产品入口和优先级已经重排。

## 5. 不写死架构原则

后续不得：

- 把三入口写死在 `App.tsx`；
- 把电影改编和小说改编塞进 `script_service.py`；
- 把所有 prompt 混用；
- 把已取消的 Assistant 历史方案继续塞回当前版本；
- 把 Document Import / Export 塞进 `upload_service`；
- 把 Prompt 功能和三入口生成页混成一个页面；
- 让返回箭头清空状态；
- 让 `source_mode` 丢失；
- 让用户上传文件进入 Git。

后续必须：

- 使用清晰的 `source_mode`；
- 每个入口有独立 prompt；
- Document import/export 独立于 upload mock；
- 当前版本不规划右侧 AI 聊天 / Assistant；
- Prompt workflow 与短剧剧本生成页分层；
- 状态保留策略先于复杂页面切换实现。

## 6. 推荐模块边界

### 后端

建议模块边界：

- `script_generation`：三入口主生成；
- `adaptation`：电影剧本、小说等来源改编；
- `documents`：导出、导入、文档版本；
- `usage_ledger`：内部试用的模型调用与成本线索；
- `quality_review`：生成剧本和改编结果的质量评审；
- `workflow / next actions`：下一步跳转和 payload 映射。

### 前端

建议模块边界：

- `creation`：三入口选择、三入口表单、短剧剧本结果；
- `documents`：导出按钮、导入面板、版本提示；
- `quality-review`：剧本质量检查、短剧节奏评估、改编质量反馈；
- `prompt-workflow`：切分 / 分镜 / Prompt 下一大功能；
- `common`：字数提示、状态 badge、通用卡片；
- `layout`：AppShell、Sidebar、Toast。

### Prompt

Prompt 边界：

- 每个入口独立 prompt；
- Prompt workflow 独立 prompt；
- 每个 prompt 文件必须版本化；
- LLM 调用记录 `source_mode` 和 prompt version。

## 7. 核心数据抽象

建议后续逐步统一以下抽象：

- `source_mode`；
- `project_id`；
- `workspace_id`；
- `session_id`；
- `user_id`；
- `ShortDramaScriptOutput`；
- `DocumentVersion`；
- `NextWorkflowPayload`。

说明：

- 这些抽象后续要逐步进入后端 Schema 和前端 types；
- 不要求一次性全部实现；
- 但新增代码时应优先对齐这些方向，避免重复造多个不兼容结构。

## 8. 当前版本取消 AI Assistant

当前版本不做右侧 AI 聊天界面、AssistantPanel、`/api/assistant/chat` 或 `suggested_actions`。

取消原因：

- 老板已明确当前版本不需要右侧聊天协作；
- 三入口真实模型生成、在线编辑、导入导出和质量加固优先级更高；
- Assistant 会引入额外 schema / service / endpoint / prompt / 上下文隔离成本；
- 在当前阶段继续规划 Assistant 会让路线图和老板决策冲突。

当前替代重点：

- 在线编辑：用户直接审看和修改生成结果；
- 质量评审：评估剧本可用性、短剧节奏、改编质量；
- 用量记录：记录 provider / model / purpose / 调用成本线索；
- 下一步工作流：将当前有效剧本带入“短剧剧本 → 分镜 → Prompt”。

历史 Assistant 文档只保留为归档，不进入当前实施路线。

## 9. 文档往返边界

Document Round-trip 包含：

- 在线编辑；
- 下载 DOCX；
- 上传修改稿；
- metadata；
- version；
- `source_stage`；
- `target_stage`。

第一版建议顺序：

1. 可以先 TXT / JSON；
2. 再 DOCX；
3. 再 import；
4. 再 metadata；
5. 再版本回溯。

边界：

- Document import/export 不应塞进 upload mock；
- 上传文件不进入 Git；
- 用户编辑后的内容优先于 AI 初始输出；
- 进入 Prompt workflow 时应使用最新编辑版本。

## 10. 前端页面层级

未来页面层级：

- Login / Mock Login；
- Entry Selection；
- Script Generation / Adaptation Page；
- Script Result / Editor Page；
- Prompt Workflow Page；
- 质量评审；
- 用量记录；
- Document Import / Export Panel。

导航规则：

- Prompt 页面左上角返回箭头回到 Script Result / Editor Page；
- 返回不是回三入口首页；
- 返回不清空用户输入、生成结果或编辑状态；
- Sidebar 是全局切换，返回箭头是局部回到上一阶段。

## 11. 后续小闭环路线

从第 188 步开始建议路线：

- 第 188 步：三入口 Schema；
- 第 189 步：`source_mode` registry 设计；
- 第 190 步：电影剧本改短剧 prompt；
- 第 191 步：小说改短剧 prompt；
- 第 192 步：电影改短剧 mock service；
- 第 193 步：小说改短剧 mock service；
- 第 194 步：endpoint；
- 第 195 步：后端测试；
- 第 196 步：前端 Entry Selection 组件；
- 第 197 步：CreationEntryModal；
- 第 198 步：三入口表单；
- 第 199 步：统一 ShortDramaScriptResult；
- 第 200 步：DOCX 下载策略；
- 第 201 步：在线编辑基础；
- 第 202 步：Document Import / Export 闭环；
- 第 203 步：UsageLedger；
- 第 204 步：质量评审；
- 第 205 步：真实 LLM 接入；
- 第 206 步：市场试用验收。

每一步都要：

- 有明确输入 / 输出；
- 有边界；
- 有测试或构建验证；
- 不顺手做无关重构。

## 12. 产品化完成标准

### 老板演示版

必须满足：

- 三入口清晰；
- 灵感入口可跑；
- 电影 / 小说入口至少 mock；
- 输入限制；
- 基础导出；
- 当前版本明确取消 Assistant。

### 市场试用版

必须满足：

- 三入口真实 LLM；
- 在线编辑；
- DOCX 下载；
- 上传；
- 用量记录；
- 质量评审；
- 数据不串；
- 测试和 build 通过；
- 文档完整。

### 公网部署版

另开部署阶段处理：

- 服务器；
- 域名；
- 备案；
- HTTPS；
- 安全组；
- WAF / CDN / DDoS 基础防护；
- 日志和备份。

公网部署不是 Phase 5A 当前小闭环的默认目标。

## 13. 当前估算步数

从当前开始估算：

- 本地老板演示版：约 35～45 小闭环；
- 小范围市场试用版：约 55～75 小闭环；
- 公网部署上线版：约 90～120 小闭环。

说明：

- 步数多是因为这是产品级平台，不是 demo；
- 每一步都要可测试、可回滚；
- 不建议为了“快点看起来完整”牺牲结构和边界；
- 服务器部署、真实账号体系和公网安全应单独开阶段。

## 14. 验收标准

- 文档明确 Phase 5A / 5B 边界；
- 文档明确三入口主线；
- 文档明确当前版本取消 Assistant；
- 文档明确 Document Round-trip；
- 文档明确 Prompt 页面返回箭头；
- 文档明确不写死架构；
- 文档明确后续路线和步数；
- 不修改代码；
- 不包含敏感信息。
