# Phase 5A Productization Execution Plan｜第五阶段 A：产品化执行蓝图

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
- 用 AI Assistant 辅助编剧决策；
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
- Assistant 辅助改写 / 改编；
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
- 把 Assistant 当普通聊天框；
- 把 Document Import / Export 塞进 `upload_service`；
- 把 Prompt 功能和三入口生成页混成一个页面；
- 让返回箭头清空状态；
- 让 `source_mode` 丢失；
- 让用户上传文件进入 Git。

后续必须：

- 使用清晰的 `source_mode`；
- 每个入口有独立 prompt；
- Assistant 独立于主生成链路；
- Document import/export 独立于 upload mock；
- Prompt workflow 与短剧剧本生成页分层；
- 状态保留策略先于复杂页面切换实现。

## 6. 推荐模块边界

### 后端

建议模块边界：

- `script_generation`：三入口主生成；
- `adaptation`：电影剧本、小说等来源改编；
- `assistant`：编剧助手 / 改编助手 / 工作流助手；
- `documents`：导出、导入、文档版本；
- `workflow / next actions`：下一步跳转、payload 映射、suggested actions。

### 前端

建议模块边界：

- `creation`：三入口选择、三入口表单、短剧剧本结果；
- `assistant`：AssistantPanel、消息列表、输入框、suggested actions；
- `documents`：导出按钮、导入面板、版本提示；
- `prompt-workflow`：切分 / 分镜 / Prompt 下一大功能；
- `common`：字数提示、状态 badge、通用卡片；
- `layout`：AppShell、Sidebar、Toast。

### Prompt

Prompt 边界：

- 每个入口独立 prompt；
- Assistant 独立 prompt；
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
- `AssistantContext`；
- `SuggestedAction`；
- `NextWorkflowPayload`。

说明：

- 这些抽象后续要逐步进入后端 Schema 和前端 types；
- 不要求一次性全部实现；
- 但新增代码时应优先对齐这些方向，避免重复造多个不兼容结构。

## 8. AI Assistant 边界

Assistant 是编剧助手 / 改编助手 / 工作流助手。

必须：

- 独立 schema；
- 独立 service；
- 独立 endpoint；
- 独立 prompt；
- 独立 env；
- 通过 `suggested_actions` 影响主流程；
- 用户确认后才应用；
- 不能自动覆盖用户编辑内容；
- 不能跨项目读取上下文。

Assistant 可以做：

- 改写灵感；
- 提炼电影剧本改编策略；
- 梳理小说人物关系；
- 增强短剧钩子；
- 给出下一步建议；
- 帮用户进入切分 / 分镜 / Prompt。

Assistant 不能做：

- 自动替用户提交生产结果；
- 自动清空编辑内容；
- 自动跨项目读取上下文；
- 和主生成链路共用业务 prompt。

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
- Assistant Panel；
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
- 第 201 步：AI Assistant 设计更新；
- 第 202 步：Assistant Schema；
- 第 203 步：Assistant mock endpoint；
- 第 204 步：前端 AssistantPanel；
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
- Assistant 规划清楚。

### 市场试用版

必须满足：

- 三入口真实 LLM；
- 在线编辑；
- DOCX 下载；
- 上传；
- Assistant mock / LLM；
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
- 文档明确 Assistant 不能忘；
- 文档明确 Document Round-trip；
- 文档明确 Prompt 页面返回箭头；
- 文档明确不写死架构；
- 文档明确后续路线和步数；
- 不修改代码；
- 不包含敏感信息。
