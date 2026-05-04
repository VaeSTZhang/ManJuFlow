# Short Drama Script Online Editing Design｜短剧剧本在线编辑设计

## 1. 背景与目标

Dramora 当前已经能通过三入口生成统一的 `ShortDramaScriptOutput`：

- 灵感生成短剧剧本；
- 电影剧本改编短剧本；
- 小说 / 网文改编短剧本。

但公司内部真实使用时，用户不会只下载 AI 原始结果。编剧、策划和老板审看时，通常需要在线微调标题、故事梗概、人物、人设、分集内容、场景和对白，然后再导出 Word / TXT / JSON，或继续进入后续“短剧剧本 → 分镜 → Prompt”工作流。

本设计用于定义第一版在线编辑能力的状态边界、交互原则、导出策略和后续集成方式。目标是让生成结果可审看、可修改、可导出、可继续流转，同时避免直接破坏 AI 原始输出和后端契约。

## 2. 在线编辑边界

第一版只做：

- 前端本地编辑状态；
- 普通 input / textarea 编辑；
- 生成结果与编辑稿分离；
- 编辑稿用于导出和后续工作流；
- 不改变后端 `ShortDramaScriptOutput` 契约；
- 不直接覆盖 `original_output`，保留 AI 原始结果。

第一版不做：

- 不接数据库；
- 不做多人协作；
- 不做自动保存；
- 不做历史版本库；
- 不做富文本编辑器；
- 不做服务端持久化；
- 不做员工账号权限与审计。

## 3. 推荐状态模型

建议在前端维护：

```ts
generatedScript: ShortDramaScriptOutput | null
editableScript: ShortDramaScriptOutput | null
isEditingScript: boolean
hasUnsavedScriptEdits: boolean
lastEditedAt?: string
```

语义：

- `generatedScript` 表示 AI 原始结果；
- `editableScript` 表示用户当前编辑稿；
- `isEditingScript` 表示结果区是否进入编辑状态；
- `hasUnsavedScriptEdits` 表示当前编辑稿相对上次保存存在未确认修改；
- `lastEditedAt` 记录最近一次保存或应用编辑的时间。

使用策略：

- 展示只读结果时，优先显示 `editableScript ?? generatedScript`；
- 导出、继续分镜、质量评审和后续工作流默认使用 `editableScript`；
- 如果 `editableScript` 为空，则使用 `generatedScript`；
- `generatedScript` 不应被普通编辑动作直接覆盖；
- “恢复为 AI 原始结果”应从 `generatedScript` 重新生成 `editableScript`。

## 4. 编辑范围第一版

当前实际 `ShortDramaScriptOutput` 字段包括：

- `project_title`
- `source_mode`
- `logline`
- `world_setting`
- `characters`
- `adaptation_notes`
- `episode_count`
- `episodes`
- `metadata`

第一版建议支持编辑：

- `project_title`：项目标题；
- `logline`：故事梗概 / 核心卖点；
- `world_setting`：世界观 / 故事背景；
- `characters[].name`；
- `characters[].role`；
- `characters[].age`；
- `characters[].personality`；
- `characters[].arc`；
- `episodes[].title`；
- `episodes[].summary`；
- `episodes[].hook`；
- `episodes[].scenes[].location`；
- `episodes[].scenes[].time`；
- `episodes[].scenes[].description`；
- `episodes[].scenes[].dialogues[].character`；
- `episodes[].scenes[].dialogues[].line`；
- `episodes[].scenes[].visual_notes`；
- `episodes[].scenes[].emotion_curve`。

第一版暂不编辑：

- `source_mode`；
- `episode_count`，除非后续支持增删集；
- `adaptation_notes`，可以先只读展示；
- `metadata`，只展示或隐藏，不开放普通用户编辑。

如果后续需要编辑 `adaptation_notes`，应单独设计“改编策略备注”编辑区，避免混入主剧情编辑。

## 5. UI 交互建议

结果区应提供：

- “开始编辑”
- “保存本次修改”
- “放弃修改”
- “恢复为 AI 原始结果”
- “复制 JSON”
- “下载 TXT”
- “下载 JSON”
- “下载 Word”

第一版可以使用普通 input / textarea：

- 标题使用 input；
- `logline` / `world_setting` 使用 textarea；
- 人物字段使用紧凑表单；
- 分集和场景继续用当前层级结构展示；
- 对白可使用每句一行的 textarea 或逐条 input；
- 不引入富文本编辑器。

交互原则：

- 点击“开始编辑”后，从当前展示结果生成 `editableScript`；
- 点击“保存本次修改”后退出编辑状态，并更新 `lastEditedAt`；
- 点击“放弃修改”后丢弃未保存编辑，回到上次保存稿；
- 点击“恢复为 AI 原始结果”需要二次确认；
- 保存和放弃只影响前端本地状态，不调用后端。

## 6. 导出策略

导出对象默认使用：

```ts
editableScript ?? generatedScript
```

规则：

- JSON / TXT / Word 应默认导出 `editableScript`；
- 如果没有编辑稿，则导出 `generatedScript`；
- “复制 JSON”也应复制当前有效稿，而不是固定复制 AI 原始稿；
- Word 导出接入前，按钮继续保持真实状态提示；
- 导出前不应把真实客户内容写入仓库或日志。

导出文件 metadata 可记录：

- `edited: true | false`
- `original_generated_at`
- `last_edited_at`
- `source_mode`
- `provider`
- `model`
- `purpose`

这些 metadata 应用于追踪来源，不应包含 API Key、完整本机路径或敏感服务器信息。

## 7. 后续分镜 / Prompt 策略

进入“短剧剧本 → 分镜 → Prompt”下一大功能时，应使用：

```ts
editableScript ?? generatedScript
```

要求：

- 后续分镜 / Prompt 工作区不能默认使用过期 AI 原始稿；
- 从结果页进入下一步时，应携带当前有效剧本 payload；
- 返回剧本结果页时必须保留用户输入、`generatedScript`、`editableScript`、`source_mode`、`selected_model`；
- 不允许因为切换页面清空用户编辑；
- 如果存在未保存编辑，跳转前应提示用户保存或继续使用当前编辑稿。

## 8. 当前版本不接入右侧聊天式 Assistant

老板已明确取消当前版本的右侧聊天式 AI Assistant 功能。因此在线编辑第一版不接入：

- AssistantPanel；
- `/api/assistant/chat`；
- `suggested_actions`；
- 聊天式改稿；
- 自动改稿动作。

当前版本的编辑策略是：用户直接在线审看和修改 `editableScript`，导出与后续工作流使用当前有效稿。

这不代表取消 AI 改写、扩写或质量评审。后续相关能力应作为剧本编辑区、质量评审区或局部操作能力接入，例如“扩写本场”“强化钩子”“优化对白”“评审短剧节奏”，而不是作为通用右侧聊天窗口接入。

如果未来重新恢复 Assistant 需求，必须重新立项，并遵守以下边界：

- 只能提出修改建议；
- 必须用户确认后才写入 `editableScript`；
- 不得自动覆盖 `generatedScript`；
- 不得跨项目读取上下文；
- 不得在用户未确认时自动修改已保存编辑稿。

## 9. 自动化测试策略

后续实现在线编辑时应补：

- `npm run build`
- `npm run test:e2e`

建议 e2e 覆盖：

- 生成结果区出现；
- 点击“开始编辑”；
- 修改标题；
- 保存本次修改；
- 结果区显示编辑后的标题；
- 复制 JSON 使用编辑后的内容；
- 下载 TXT 使用编辑后的内容；
- 放弃修改恢复上次保存稿；
- 恢复为 AI 原始结果；
- 页面没有开发态文案。

如果后续接 Word 导出，还应增加：

- 编辑后 Word 导出使用当前有效稿；
- 没有编辑稿时 Word 导出使用 AI 原始稿；
- 导出按钮在未接入真实服务前保持禁用或明确提示。

## 10. 分步实施建议

建议后续小步推进：

1. 第 253 步：拆 `ShortDramaScriptResult` 结果操作区或编辑设计类型；
2. 第 254 步：前端 `editableScript` state 接入 `CreationHome`；
3. 第 255 步：`ShortDramaScriptResult` 支持标题 / logline 基础编辑；
4. 第 256 步：编辑后复制 JSON / 下载 TXT 使用 `editableScript`；
5. 第 257 步：编辑后 Word 导出策略；
6. 第 258 步：e2e 覆盖在线编辑基础流程。

每一步都应保持：

- 不改后端契约；
- 不接数据库；
- 不引入富文本编辑器；
- `npm run build` 通过；
- `npm run test:e2e` 通过；
- `git diff` 范围清晰。

## 11. 不做事项

本轮在线编辑不做：

- 不引入富文本编辑器；
- 不引入复杂状态管理；
- 不接数据库；
- 不做协同编辑；
- 不做版本树；
- 不做自动保存；
- 不做真实员工账号权限；
- 不做 Assistant 自动改稿；
- 不做复杂增删集 / 增删场；
- 不把编辑状态写入 `metadata` 后再反向解析为业务内容；
- 不在公开仓库提交真实客户剧本。

## 12. 当前建议下一步

建议第 253 步先做前端类型 / 状态接入，而不是一口气做完整编辑器。

更稳的下一步是：

- 在 `CreationHome` 中区分 `generatedScript` 和 `editableScript`；
- 明确当前有效稿选择函数；
- 保持 `ShortDramaScriptResult` 先只读展示；
- 让复制 JSON / 下载 TXT 后续能统一切到当前有效稿。

这样可以先建立在线编辑的数据基础，再逐步打开标题、logline、人物和分集内容的编辑 UI。
