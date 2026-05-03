# Frontend Information Architecture Plan｜前端信息架构升级方案

## 1. 文档定位

当前前端已经完成 MVP 链路，能够从灵感输入推进到结构化剧本、分镜、绘图 Prompt、Image Generation mock、Bundle、Assets 和 Tasks 展示。

但随着第四阶段继续补齐 ImageGeneration、Asset Manager、Task Center 和未来 ComfyUI 能力，`App.tsx` 正在变大，页面也从早期 MVP 的单页纵向展示逐渐变成多功能工作台。

本文档用于先规划前端信息架构、UI 布局和组件拆分边界，不直接改代码，不引入 UI 库，也不改变当前业务链路。

## 2. 当前问题

当前前端主要问题：

- 所有功能堆在一个页面；
- 剧本、分镜、Prompt、ImageGeneration、Assets、Tasks 信息密度越来越高；
- 错误提示分散在各个表单和结果区域；
- 用户无法快速切换功能模块；
- 后续接 Asset Manager / Task Center / ComfyUI 后页面会更加拥挤；
- `App.tsx` 继续膨胀会增加维护成本；
- 跨模块状态、复制导出状态、错误状态混在同一个组件中，后续难以测试和维护。

## 3. 目标 UI 结构

建议从单页纵向堆叠升级为现代工作台式布局：

- 左侧 `Sidebar`：功能导航；
- 右侧 `Main Workspace`：展示当前选中的功能模块；
- 顶部状态栏或系统状态区：展示后端连接、运行模式、当前阶段；
- 右上角 `Toast Notification`：统一显示错误、成功、提醒和信息；
- 每个功能模块逐步拆成独立 workspace 组件。

示意结构：

```text
AppShell
├── Sidebar
│   ├── 灵感剧本
│   ├── 剧本转分镜
│   ├── 分镜转绘图 Prompt
│   ├── 图片生成
│   ├── 资产与任务
│   └── 系统状态 / 设置
├── TopBar / SystemStatus
├── MainWorkspace
│   └── 当前选中的 workspace
└── ToastContainer
```

主工作区展示逻辑：

```text
Sidebar 当前选中项
→ Main Workspace 渲染对应模块
→ 保留跨模块数据传递能力
```

## 4. Sidebar 功能入口建议

第四阶段可以先实现 4-5 个入口，不必一次做完整权限、历史记录和项目管理。

建议入口：

- `Idea → Script`：灵感输入与结构化剧本生成；
- `Script → Storyboard`：剧本转分镜；
- `Storyboard → ImagePrompt`：分镜转绘图 Prompt；
- `Image Generation`：图片生成 mock、bundle、assets/tasks 概览；
- `Assets / Tasks`：后续独立资产与任务中心；
- `System Status`：系统状态、运行模式、后端连接信息。

初期可以先把 `Assets / Tasks` 放在 `Image Generation` 内，等功能继续增长后再拆成独立入口。

## 5. 组件拆分建议

建议未来逐步拆分为以下结构：

```text
apps/web/src/components/layout/
├── AppShell.tsx
├── Sidebar.tsx
└── Toast.tsx

apps/web/src/components/workspaces/
├── IdeaScriptWorkspace.tsx
├── StoryboardWorkspace.tsx
├── ImagePromptWorkspace.tsx
├── ImageGenerationWorkspace.tsx
├── AssetTaskWorkspace.tsx
└── SystemStatusPanel.tsx

apps/web/src/components/common/
├── ResultCard.tsx
├── JsonActions.tsx
├── FieldGroup.tsx
└── StatusBadge.tsx
```

拆分原则：

- 当前不要一步大拆完；
- 先拆布局骨架，再迁移单个 workspace；
- 保留现有数据链路；
- 优先迁移第四阶段最拥挤的 `ImageGenerationWorkspace`；
- 通用组件只在重复出现 2-3 次后再抽象。

## 6. 状态管理原则

短期状态管理继续保持轻量：

- 暂时不引入 Redux / Zustand；
- 继续使用 React `useState`；
- `App.tsx` 可以短期保留跨模块链路状态；
- workspace 内部状态逐步局部化；
- 跨模块传递可以先通过 props 完成；
- 后续如果出现复杂项目状态、历史记录或任务轮询，再评估是否引入更正式的状态管理。

当前优先级是保证功能稳定，不追求过度工程化。

## 7. Toast / Error Notification 设计

后续错误和操作反馈不应只散落在各个表单下方。建议新增右上角 Toast：

Toast 类型：

- `success`
- `error`
- `warning`
- `info`

使用场景：

- 接口失败；
- JSON 解析失败；
- 必填字段为空；
- 复制成功；
- 导出成功；
- 生成完成；
- 后端未连接；
- bundle / assets / tasks 获取失败。

初期实现原则：

- 自研轻量 Toast，不引入 UI 库；
- 支持自动消失；
- 支持手动关闭；
- 不阻塞现有表单错误提示；
- 可以先保留局部错误文案，Toast 作为统一提醒层。

## 8. 迁移策略

建议分步迁移：

- 第 130 步：新增 layout / toast 方案所需组件骨架；
- 第 131 步：实现 `AppShell` + `Sidebar`，先不迁移业务逻辑；
- 第 132 步：接入 `Toast Notification`；
- 第 133 步：将 `ImageGeneration` 区域优先迁移到 workspace；
- 第 134 步：逐步迁移 Script / Storyboard / ImagePrompt；
- 第 135 步：浏览器完整链路验收。

每一步都应保持可运行、可回退、可验证。

## 9. 风险与控制

主要风险：

- 一次性大重构导致现有链路断裂；
- 组件拆分后跨模块数据传递混乱；
- Toast 和局部错误提示重复或冲突；
- CSS 大改导致页面响应式布局退化；
- ImageGeneration / Bundle / Assets / Tasks 展示被误删或弱化。

控制策略：

- 不要一次性大重构；
- 每次只迁移一个区域；
- 每步运行 `npm run build`；
- 每步进行浏览器验收；
- 保留现有功能按钮和数据链路；
- 保留现有 `generateImages` 与 `generateImageBundle` 两条调用路径；
- 出现风险时可以回退到当前纵向布局。

## 10. 视觉风格建议

建议视觉方向：

- 现代工作台风格；
- 左侧 Sidebar 可以使用深色或浅色，但要克制；
- 右侧为内容工作区，使用清晰的表单、结果卡片和状态卡片；
- 统一按钮、输入框、卡片、状态 badge；
- 控制信息密度，避免所有字段同时压在一个视图里；
- 不追求花哨动画；
- 先做清晰、专业、可评审；
- 让非技术用户能快速理解当前在哪个阶段、下一步能做什么。

## 11. 当前不做

当前信息架构升级阶段暂不做：

- 不引入大型 UI 库；
- 不做登录权限；
- 不做数据库历史记录；
- 不做真实 ComfyUI；
- 不做复杂拖拽；
- 不做完整项目管理系统；
- 不做多用户协作；
- 不做生产级任务队列 UI；
- 不做复杂主题系统。

## 12. 验收标准

文档层面验收：

- 方案清晰；
- 迁移步骤清晰；
- 明确不影响当前功能；
- 明确不引入 UI 库；
- 后续 Codex 可以按步骤执行。

代码层面后续验收：

- `npm run build` 通过；
- 灵感 → 剧本 → 分镜 → Prompt → ImageGeneration → Bundle → Assets / Tasks 链路仍然通过；
- Sidebar 能切换工作区；
- Toast 能显示错误和成功提示；
- 原有复制、导出、带入下一阶段功能仍然可用；
- 当前 mock provider 行为不受影响；
- 不接真实 ComfyUI，不引入真实服务器配置。
