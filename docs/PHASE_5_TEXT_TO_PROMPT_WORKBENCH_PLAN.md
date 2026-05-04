# Phase 5 Text-to-Prompt Workbench Plan｜文字到媒体提示词工作台方案

## Update Note｜2026-05-04

第五阶段主产品定位已调整为“三入口短剧剧本生成与改编工作台”：

- 灵感生成短剧剧本；
- 电影剧本改编短剧剧本；
- 小说改编短剧剧本。

本文档保留为历史阶段方案和后续能力参考。Text-to-Prompt、Script Segmentation、Storyboard、ImagePrompt 链路调整为生成短剧剧本后的下一大功能预备，不再作为当前首页主入口第一优先级。

## 1. 阶段定位

第五阶段不是继续推进真实图片生成、视频生成或 GPU / ComfyUI 私有联调，而是回到当前最新业务诉求：让“灵感或已有剧本”都能通过 ManJuFlow 工作流，最终变成文字转媒体的提示词。

建议阶段命名：

```text
Phase 5｜Text-to-Prompt Workbench
第五阶段｜文字到媒体提示词工作台
```

第五阶段聚焦：

- 灵感到文字；
- 已有剧本到结构化切分；
- 文字到文字；
- 文字到媒体提示词；
- AI 聊天协作；
- 非技术人员可用的内容生产工作台。

本阶段的核心目标是把“文字生产”和“媒体提示词生产”之间的工作台体验打稳，让用户可以从灵感、已有剧本或自然语言协作入口进入，并最终汇流到 Storyboard / ImagePrompt / ImageGeneration mock 链路。

## 2. 为什么暂缓真实图片 / 视频 / GPU

第五阶段暂缓真实图片、视频、ComfyUI 和远端 GPU，原因如下：

- 最新业务诉求优先级是“文字到媒体提示词”，不是直接成片；
- 已有剧本输入还没有被系统化支持；
- 非技术人员还缺少自然语言协作入口；
- 真实 GPU / ComfyUI 会引入服务器、安全、成本、workflow 私有化等复杂问题；
- 当前公开仓库应继续保持 mock、接口、抽象和文档边界；
- 先把文字生产、切分、Prompt 链路打稳，后续再接真实生成更稳。

第四阶段已经完成 ImageGeneration mock / bundle / assets / tasks 和工作台 UI，足以支撑公开仓库评审。第五阶段不应为了“看起来更像生产系统”而提前接真实 GPU。真实生成应等 Script Segmentation、Assistant、workflow registry mock、Asset / Task 规则进一步稳定后，再按私有 checklist 决策。

## 3. 当前项目已具备的前置能力

### Phase 1：Idea → Script

已完成：

- 灵感输入；
- 结构化短剧剧本输出；
- `POST /api/scripts/generate`；
- 前端展示、复制、导出 JSON；
- mock / llm 模式。

### Phase 2：Script → Storyboard

已完成：

- 剧本转导演分镜；
- `StoryboardOutput`；
- `POST /api/storyboards/generate`；
- 前端分镜展示；
- 剧本结果一键带入分镜；
- 分镜 JSON 复制 / 导出。

### Phase 3：Storyboard → ImagePrompt

已完成：

- 分镜转 AI 绘图 Prompt；
- `ImagePromptInput` / `ImagePromptItem` / `ImagePromptOutput`；
- `POST /api/prompts/generate`；
- 多文本 LLM provider；
- 前端 ImagePrompt 模型选择器；
- 绘图 Prompt JSON 展示、复制、导出。

### Phase 4：ImagePrompt → ImageGeneration Mock / Bundle / Asset / Task / Workspace

已完成：

- ImageGeneration mock；
- Asset / RenderTask；
- `ImageGenerationBundleOutput`；
- `POST /api/images/generate`；
- `POST /api/images/generate-bundle`；
- AppShell + Sidebar 工作台布局；
- Toast；
- Workspace 切换；
- ComfyUI / 远端 GPU 私有部署文档与安全边界。

## 4. 第五阶段核心目标

第五阶段核心目标：

1. 新增“已有剧本切分”能力  
   用户可以粘贴已有剧本或后续上传文本文件，系统切分为结构化片段。

2. 切分结果进入现有链路  
   `Script Segments` → `Storyboard` → `ImagePrompt` → `ImageGeneration Mock / Bundle`。

3. 新增右侧 AI Assistant 聊天协作面板  
   非技术人员可以自然语言要求 AI 改写、拆分、补全、增强钩子、生成 Prompt、切换工作区。

4. 建立 Assistant suggested actions  
   让 AI 回复不只是聊天文本，还能返回可执行建议，例如：

   - 切换工作区；
   - 将当前剧本带入切分；
   - 将切分结果带入分镜；
   - 将分镜带入 Prompt；
   - 应用改写结果；
   - 复制 / 导出建议。

5. 保持 mock 优先  
   先以 mock service 和固定 suggested actions 跑通前后端链路，再考虑 LLM 模式。

## 5. 三个入口与统一汇流

第五阶段工作台建议包含三个入口。

### 入口 A：灵感输入

沿用已有链路：

```text
Idea
  -> ScriptOutput
  -> StoryboardOutput
  -> ImagePromptOutput
```

### 入口 B：已有剧本输入

新增链路：

```text
Existing Script
  -> Script Segmentation
  -> StoryboardOutput
  -> ImagePromptOutput
```

### 入口 C：AI 聊天协作

新增 Assistant Panel：

```text
User natural language
  -> Assistant reply
  -> suggested_actions
  -> apply with confirmation
  -> workspace / data update
```

统一汇流目标：

无论用户从灵感、已有剧本还是聊天入口开始，最终都应该进入：

- 结构化剧本 / 切分片段；
- `StoryboardOutput`；
- `ImagePromptOutput`；
- 后续 Media Prompt / ImageGeneration mock。

## 6. 已有剧本切分模块设计

后续建议新增：

```text
apps/api/app/schemas/script_segmentation.py
```

建议 Schema：

- `ExistingScriptInput`
- `ScriptSegment`
- `ScriptSegmentationOutput`

### ExistingScriptInput

建议字段：

- `project_title`
- `script_text`
- `source_type`
- `target_segment_level`
- `language`
- `extra_requirements`

### ScriptSegment

建议字段：

- `segment_id`
- `episode_number`
- `scene_number`
- `segment_type`
- `title`
- `original_text`
- `summary`
- `characters`
- `location`
- `time_of_day`
- `conflict`
- `emotion`
- `visual_notes`
- `dialogue_text`
- `estimated_duration_seconds`
- `next_step_hint`

### ScriptSegmentationOutput

建议字段：

- `project_title`
- `segmentation_summary`
- `segment_count`
- `segments`
- `metadata`

### 后端文件建议

- `apps/api/app/services/script_segmentation_service.py`
- `apps/api/app/routers/scripts.py` 或独立 router
- `POST /api/scripts/segment`

### 测试文件建议

- `tests/api/test_script_segmentation_schema.py`
- `tests/api/test_script_segmentation_service.py`
- `tests/api/test_script_segmentation_endpoint.py`

### 前端文件建议

- `apps/web/src/types/scriptSegmentation.ts`
- `apps/web/src/api/scriptSegmentation.ts`
- `ScriptSegmentationWorkspace`

## 7. AI Assistant Panel 设计

后续建议在前端右侧新增 AI Assistant Panel。

建议能力：

- 可展开 / 收起；
- 展示消息列表；
- 支持输入自然语言；
- 支持上下文感知；
- 支持 suggested actions；
- 不一开始做复杂多 Agent；
- 不一开始做流式输出；
- 不一开始接真实 LLM；
- 先 mock。

前端建议目录：

```text
apps/web/src/components/assistant/
├── AssistantPanel.tsx
├── AssistantMessageList.tsx
├── AssistantComposer.tsx
└── AssistantSuggestedActions.tsx
```

前端类型：

```text
apps/web/src/types/assistant.ts
```

前端 API：

```text
apps/web/src/api/assistant.ts
```

## 8. Assistant 后端设计

后续建议新增：

```text
apps/api/app/schemas/assistant.py
```

建议 Schema：

- `AssistantContext`
- `AssistantChatInput`
- `AssistantSuggestedAction`
- `AssistantChatOutput`

### AssistantChatInput

建议字段：

- `project_title`
- `user_message`
- `current_workspace`
- `context`
- `selected_text`
- `intent_hint`
- `provider`
- `model`

### AssistantContext

建议包含：

- `idea`
- `script_output`
- `script_segments`
- `storyboard_output`
- `image_prompt_output`
- `image_generation_bundle`

### AssistantSuggestedAction

建议字段：

- `action_type`
- `label`
- `target_workspace`
- `payload`
- `confidence`
- `requires_confirmation`

### AssistantChatOutput

建议字段：

- `reply`
- `suggested_actions`
- `updated_fields`
- `metadata`

后端 service：

```text
apps/api/app/services/assistant_service.py
```

后端 endpoint：

```text
POST /api/assistant/chat
```

环境变量后续可预留：

```env
ASSISTANT_GENERATION_MODE=mock / llm
```

## 9. 第五阶段明确暂不做

第五阶段早期明确暂不做：

- 暂不接真实客户数据；
- 暂不接真实生产剧本；
- 暂不上传真实公司素材；
- 暂不接真实 ComfyUI / GPU；
- 暂不做文生视频；
- 暂不做完整多 Agent；
- 暂不引入 Redis / Celery / MinIO；
- 暂不引入复杂全局状态管理；
- 暂不做权限系统；
- 暂不做用户账号系统；
- 暂不做生产部署；
- 暂不把聊天做成无限制自动执行系统；
- 暂不让 Assistant 自动修改生产数据，所有应用动作都应先显式确认。

## 10. 公开仓库安全边界

公开仓库可以包含：

- Script Segmentation Schema；
- Script Segmentation mock service；
- Script Segmentation endpoint；
- Assistant Schema；
- Assistant mock service；
- Assistant endpoint；
- 前端 mock UI；
- suggested actions 的占位结构；
- 不含敏感信息的虚构样例；
- 文档和本地 demo。

公开仓库不能包含：

- API Key；
- `.env`；
- 真实客户剧本；
- 合作方敏感资料；
- 个人隐私；
- 真实服务器地址；
- 模型权重；
- 私有 workflow；
- 公司内部生产素材；
- 未脱敏聊天记录。

公开仓库的定位仍然是可评审架构、本地 mock demo、数据协议和安全集成边界。

## 11. Mock 优先策略

第五阶段继续坚持 mock 优先：

- Script Segmentation 先 mock；
- Assistant Chat 先 mock；
- suggested actions 先固定枚举；
- 前端先验证布局、交互、状态传递；
- 后端先验证 Schema / service / endpoint；
- 等数据协议和 UI 体验稳定后，再接 LLM 模式。

mock 优先不是降低质量，而是为了先稳定产品交互、数据契约和安全边界，避免在 UI 和协议尚未定型时引入真实模型成本与不确定性。

## 12. 前端信息架构原则

第五阶段不能大重构，但要避免页面继续变大。

前端原则：

- 保持 AppShell + Sidebar；
- 新增“已有剧本切分” workspace；
- 右侧 AssistantPanel 先可展开 / 收起；
- 不一次性引入复杂状态管理；
- 先用现有 React state / props；
- 如果状态明显失控，再单独规划状态管理；
- 不把所有逻辑继续堆进单个组件；
- 新增组件尽量放在 `components/workspaces` 和 `components/assistant`。

第五阶段的前端改造应沿用第四阶段的渐进式策略：先搭骨架，再接 mock，再做浏览器验收，最后再考虑更深的组件拆分。

## 13. 第五阶段建议步骤

建议按当前项目步数继续推进：

- 第 140 步：新增 Phase 5 方案文档；
- 第 141 步：新增已有剧本切分 Schema；
- 第 142 步：新增 script segmentation mock service；
- 第 143 步：新增 `POST /api/scripts/segment`；
- 第 144 步：新增 Script Segmentation 后端测试；
- 第 145 步：前端新增 ScriptSegmentation 类型和 API；
- 第 146 步：Sidebar 新增“已有剧本切分” workspace；
- 第 147 步：已有剧本切分结果带入 Storyboard / ImagePrompt；
- 第 148 步：新增 `AI_ASSISTANT_PANEL_DESIGN.md`；
- 第 149 步：Assistant Chat Schema / mock service / endpoint；
- 第 150 步：前端右侧 AssistantPanel mock UI；
- 第 151 步：Assistant suggested actions；
- 第 152 步：文档更新 API_CONTRACT / LOCAL_DEV / MVP_ROADMAP；
- 第 153 步：阶段性浏览器验收；
- 第 154 步：Phase 5 中期总结。

## 14. 验收标准

第 140 步验收标准：

- `docs/PHASE_5_TEXT_TO_PROMPT_WORKBENCH_PLAN.md` 已新增；
- 文档明确第五阶段定位；
- 文档明确为什么暂缓真实图片 / 视频 / GPU；
- 文档明确三个入口：灵感、已有剧本、AI 聊天；
- 文档明确最终汇入 Prompt 生成链路；
- 文档包含已有剧本切分模块设计；
- 文档包含 AI Assistant Panel 设计；
- 文档包含公开仓库安全边界；
- 文档明确 mock 优先；
- 文档明确不接真实客户数据；
- 文档明确不引入复杂状态管理；
- 文档明确不一次性大重构；
- 不修改代码；
- 不引入敏感信息。
