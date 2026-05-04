# Three-entry to Prompt Navigation Design｜三入口到 Prompt 页面导航设计

## 1. 文档目的

本文档用于明确三入口短剧剧本生成大功能与下一大功能“文字转 Prompt / 切分 / 分镜 / Prompt”之间的页面导航关系，尤其是 Prompt 页面左上角返回箭头和状态保留逻辑。

核心问题：

- 用户不是在三入口首页左上角返回；
- 用户是在进入下一大功能页面后，需要返回上一阶段的短剧剧本生成 / 改编结果页；
- 返回后不能清空用户输入、生成结果、在线编辑内容和当前上下文。

本文件只做产品和技术边界设计，不改代码。

## 2. 产品层级

当前产品层级建议如下。

一级：

- 登录 / mock login；
- 三入口选择页。

二级：

- 短剧剧本生成 / 改编页面：
  - 灵感生成短剧；
  - 电影剧本改短剧；
  - 小说改短剧。

三级 / 下一大功能：

- 短剧剧本切分；
- 分镜；
- 绘图 / 媒体 Prompt。

说明：

- Prompt 不是三入口首页里的一个小区域；
- Prompt 是用户生成短剧剧本之后可进入的下一大功能页面；
- 三入口页面负责“生成 / 改编短剧剧本”；
- 下一大功能页面负责“把短剧剧本继续切分、分镜、转 Prompt”。

## 3. 返回箭头位置

返回箭头位置必须明确：

- 返回箭头位于“Prompt / 切分 / 分镜”功能页面左上角；
- 不是位于三入口选择页；
- 不是位于登录页；
- 返回目标是上一阶段的短剧剧本生成 / 改编结果页；
- 返回后用户可以继续编辑剧本、重新下载 DOCX、重新进入 Prompt 功能。

建议文案：

```text
← 返回短剧剧本
```

或：

```text
← 返回剧本生成结果
```

如果用户来自电影剧本改编或小说改编，返回目标仍是对应的“短剧剧本生成 / 改编结果页”，而不是三入口选择页。

## 4. 状态保留要求

返回时必须保留：

- 当前用户；
- 当前 `project_id`；
- 当前 `workspace_id`；
- 当前 `source_mode`；
- 用户选择的入口；
- 用户输入内容；
- 生成的 `ShortDramaScriptOutput`；
- 用户在线编辑后的文本；
- 下载 / 导出状态；
- 进入 Prompt 前生成的上下文 payload；
- Prompt 页面生成结果可选保留。

不能出现：

- 返回后入口选择清空；
- 返回后输入内容丢失；
- 返回后生成剧本丢失；
- 返回后编辑内容回到 AI 初始版本；
- 返回后 `source_mode` 丢失；
- 返回后用户不知道自己从哪个入口进入。

状态保留的优先级：

1. 用户在线编辑后的文本；
2. 生成的短剧剧本结构；
3. 当前入口和 source_mode；
4. Prompt 页面中已生成的中间结果；
5. 下载 / 导出状态。

## 5. 第一版前端状态策略

第一版可以使用：

- React state；
- `localStorage`；
- workspace-level draft cache。

建议状态对象：

- `currentEntry`；
- `scriptDraftByEntry`；
- `generatedScriptByEntry`；
- `editedScriptByEntry`；
- `promptWorkflowState`；
- `lastVisitedWorkspace`；
- `projectContext`。

示意：

```text
projectContext
├── project_id
├── workspace_id
├── user_id
├── session_id
└── source_mode

scriptDraftByEntry
├── idea
├── film_script
└── novel

editedScriptByEntry
├── idea
├── film_script
└── novel
```

说明：

- 第一版不需要上 Redux / Zustand 等复杂状态管理库；
- 但也不能把所有状态塞死在单个组件里；
- 三入口表单状态和 Prompt 页面状态应有清晰边界；
- 返回箭头只改变当前 workspace / page，不应清空 draft cache。

## 6. 后续持久化策略

市场试用版后续应逐步迁移到：

- `project_id`；
- `workspace_id`；
- `session_id`；
- `user_id`；
- SQLite；
- document version metadata；
- quality review metadata。

目标：

- 刷新页面后可恢复；
- 切换设备后可恢复；
- 返回上一阶段后仍能看到最新编辑内容；
- 质量评审和后续工作流能读取正确上下文；
- UsageLedger 能按项目和 workspace 统计。

长期建议：

- 本地开发阶段：`localStorage` + mock metadata；
- 市场试用阶段：SQLite；
- 私有部署阶段：PostgreSQL / 私有对象存储 / 权限系统。

## 7. 与 Sidebar 的关系

Sidebar 可以保留，但需要明确职责：

- 三入口首页是主引导；
- Prompt / 切分 / 分镜是独立 workspace；
- 返回箭头是局部返回上一阶段，不等同于 Sidebar 全局切换；
- Sidebar 切换时也要尽量保留状态。

建议：

- Sidebar 用于全局 workspace 切换；
- Prompt 页面左上角返回箭头用于“返回当前项目的短剧剧本结果页”；
- 如果用户通过 Sidebar 切走，再回来，也应尽量恢复当前页面状态；
- 不应让 Sidebar 切换把剧本结果清空。

## 8. 与 Document Round-trip 的关系

在短剧剧本生成结果页，用户可以：

- 在线编辑；
- 下载 DOCX；
- 上传修改稿；
- 再进入 Prompt。

Prompt 页面返回后，用户仍应能看到最新编辑后的剧本，而不是 AI 初始生成版本。

Document Round-trip 对状态保留的要求：

- 在线编辑文本必须优先于 AI 初始输出；
- 上传修改稿后应更新当前剧本草稿；
- 进入 Prompt 前应使用最新编辑版本；
- 返回后仍显示最新编辑版本；
- 导出状态和版本 metadata 后续应可追溯。

## 9. 当前版本不接入 AI Assistant

老板已明确取消当前版本的右侧 AI 聊天界面和 AI Assistant 功能。因此三入口到 Prompt 的导航设计不再包含：

- AssistantPanel；
- `/api/assistant/chat`；
- `suggested_actions`；
- 聊天式跨页面操作；
- Assistant 自动带入下一步。

当前版本的页面切换和下一步动作应通过明确按钮、明确状态 payload 和用户确认完成。

边界：

- 不自动清空用户草稿；
- 不自动覆盖用户编辑后的剧本；
- 不跨项目读取上下文；
- 不把 Prompt 页面生成结果误写回短剧剧本页；
- next workflow payload 必须带 `project_id` / `workspace_id` / `source_mode`。

## 10. 实施路线建议

建议后续按小闭环推进：

- 新增导航设计文档；
- 前端定义 workspace / route 状态模型；
- 抽出三入口结果页状态；
- 新增 Prompt 功能页面返回箭头；
- 返回时恢复短剧剧本结果；
- 接入 `localStorage` draft cache；
- 浏览器验收返回不清空；
- 后续接 SQLite 持久化。

验收时应重点检查：

- 从三入口进入 Prompt 页面；
- Prompt 页面左上角有返回箭头；
- 返回后仍显示刚才的短剧剧本；
- 在线编辑内容没有丢失；
- source_mode 没有丢失；
- 再次进入 Prompt 仍能使用最新剧本文本。

## 11. 验收标准

- 文档明确返回箭头在 Prompt 页面左上角；
- 文档明确返回目标是短剧剧本生成 / 改编结果页；
- 文档明确返回不清空状态；
- 文档明确第一版状态策略；
- 文档明确后续持久化策略；
- 文档明确与 Sidebar、Document Round-trip、质量评审和后续工作流的关系；
- 不修改代码；
- 不包含敏感信息。
