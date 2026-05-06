# Frontend App Structure Refactor Plan｜前端 App.tsx 结构治理方案

## 1. 背景

第 326 步结构审计发现：

- `apps/web/src/App.tsx` 已达 2167 行；
- `apps/web/src/components/creation/CreationHome.tsx` 约 480 行；
- `apps/web/tests/e2e/creation-home.spec.ts` 约 385 行；
- `apps/web/tests/e2e/document-round-trip.spec.ts` 约 592 行。

当前后端全量测试、前端 build 和 e2e 均已通过，说明功能处于可治理状态。此时应先制定渐进拆分方案，而不是继续把 Auth、Usage Ledger、Quality Review、Project Management 和部署前状态全部塞进 `App.tsx`。

本阶段不应一次性大重构。`App.tsx` 治理必须以小步拆分、行为不变、测试通过为基本原则。

## 1.1 当前治理状态

截至第 339 步，前端 App 第一轮结构治理已完成：

- 第 327 步：新增前端 App 结构治理方案文档；
- 第 328 步：抽出 `useAppToasts`；
- 第 329 步：抽出 `useAppAuth`；
- 第 330 步：抽出 `useWorkspaceNavigation`；
- 第 332 步：抽出 `useLegacyIdeaScriptWorkspace`；
- 第 334 步：抽出 `useStoryboardWorkspace`；
- 第 336 步：抽出 `useImagePromptWorkspace`；
- 第 338 步：抽出 `useImageGenerationWorkspace`；
- `App.tsx` 已从 2167 行降到 1465 行；
- 前端 `npm run build` 通过；
- 前端 `npm run test:e2e` 13 passed；
- 后端 `python -m pytest tests/api` 557 passed；
- git status clean。

这代表前端 App 第一轮结构治理已完成，不代表 `App.tsx` 已经彻底完美。主要 workspace orchestration 已从 `App.tsx` 拆出，后续仍可继续渐进优化，但不应为了追求完美拆分无限拖延服务器部署前准备。

## 2. 当前 App.tsx 主要职责

当前 `App.tsx` 同时承担了多类职责：

- 全局认证状态：
  - `isAuthenticated`；
  - `authContext`；
  - `isAuthLoading`。
- topbar 登录 / 登出：
  - 调用 `/api/auth/login`；
  - 设置登录态；
  - 退出登录清空登录态。
- workspace 导航：
  - `activeWorkspaceId`；
  - `Sidebar` 挂载；
  - 非当前 workspace 的访问提示。
- toast：
  - toast message state；
  - `pushToast`；
  - `dismissToast`。
- system status：
  - `/api/system/status` 请求；
  - 系统连接状态提示。
- 当前 Dramora 主线挂载：
  - `CreationHome`；
  - auth context 传入；
  - 登录门禁。
- 旧阶段工作区状态和逻辑：
  - legacy idea/script form；
  - storyboard form / result / copy / export / transfer；
  - image prompt form / result / copy / export / transfer；
  - image generation form / result；
  - image bundle / asset / task 展示。
- API 调用 orchestration：
  - scripts；
  - storyboards；
  - image prompts；
  - image generation；
  - image bundle。
- 下载 / 复制 / 转移操作：
  - JSON copy；
  - JSON export；
  - script to storyboard；
  - storyboard to prompt；
  - prompt item formatting。

这些职责已经超过一个根组件应承担的范围。后续如果继续扩展，会提高维护成本和回归风险。

## 3. 风险

如果继续把功能堆进 `App.tsx`，主要风险包括：

- Auth、Usage Ledger、Quality Review、Project Management 的状态和 handler 会与旧工作区逻辑混在一起；
- 单文件冲突风险高，多人协作时容易互相覆盖；
- 新人接手时需要先理解 2000 多行根组件，成本过高；
- e2e 失败时难以定位是 AppShell、登录、workspace、旧阶段工作区还是当前 CreationHome 主线的问题；
- 旧 ManJuFlow 阶段功能和 Dramora 当前三入口剧本工作台主线容易混杂；
- 后续部署前安全状态、权限状态、项目状态可能被临时变量写散；
- 根组件体积过大，会抑制后续小步重构和测试补充。

## 4. 拆分原则

后续治理必须遵守：

- 每次只拆一个小闭环；
- 先抽 hook，再抽组件；
- 优先不改 UI、不改行为；
- 每次拆完都运行 `npm run build` 和 `npm run test:e2e`；
- 不为了漂亮目录做无意义大搬家；
- 不引入 Redux / Zustand 等状态库；
- 不引入路由库；
- 旧功能暂缓但不随意删除，除非产品路线明确；
- 当前主线优先服务：
  - 三入口剧本生成；
  - 文本改编；
  - Word 导入；
  - 在线编辑；
  - TXT / JSON / DOCX 导出；
  - Auth；
  - Usage Ledger。

拆分时应让 `App.tsx` 逐步回到根组件职责：组装 AppShell、提供 workspace router、挂载全局 provider-like hooks。

## 5. 建议目标结构

建议逐步形成以下结构：

```text
apps/web/src/app/
├── AppRoot.tsx
├── useAppAuth.ts
├── useAppToasts.ts
└── useWorkspaceNavigation.ts
```

```text
apps/web/src/workspaces/
├── CreationWorkspace.tsx
├── LegacyIdeaWorkspace.tsx
├── StoryboardWorkspace.tsx
├── ImagePromptWorkspace.tsx
└── ImageGenerationWorkspace.tsx
```

如果旧阶段功能需要归档，可后续再评估：

```text
apps/web/src/workspaces/archive/
└── LegacyIdeaWorkspace.tsx
```

Auth 相关可逐步沉淀为：

```text
apps/web/src/features/auth/
├── useAuthSession.ts
└── authTypes.ts
```

当前已存在的通用类型也可以继续保留：

```text
apps/web/src/types/auth.ts
apps/web/src/api/auth.ts
```

Creation 相关组件和 hooks 已经完成一轮结构治理，短期不急着迁移目录：

```text
apps/web/src/components/creation/
apps/web/src/hooks/creation/
```

以上只是目标结构，不要求一次性实现。

## 6. 分阶段拆分路线

建议路线：

- 第 327 步：新增结构治理设计文档；（已完成）
- 第 328 步：抽出 `useAppToasts`；（已完成）
- 第 329 步：抽出 `useAppAuth`；（已完成）
- 第 330 步：抽出 `useWorkspaceNavigation`；（已完成）
- 第 331 步：同步结构治理文档状态；（已完成）
- 第 332 步：拆 legacy idea/script workspace orchestration；（已完成）
- 第 334 步：拆 storyboard workspace orchestration；（已完成）
- 第 335 步：同步结构治理文档状态；（已完成）
- 第 336 步：拆 image prompt workspace orchestration；（已完成）
- 第 337 步：同步结构治理文档状态；（已完成）
- 第 338 步：拆 image generation workspace orchestration；（已完成）
- 第 339 步：`App.tsx` 收敛复查；（已完成）
- 第 340 步：README / Roadmap 同步。

第 340 步之后，如有必要，可继续拆 system status、assets/tasks 展示、legacy remaining UI 等模块，但这些不应作为当前服务器部署前硬阻塞。

每一步都必须满足：

- 不改 UI；
- 不改用户行为；
- `npm run build` 通过；
- `npm run test:e2e` 通过；
- diff 范围清晰；
- git status clean 后再提交。

推荐优先级：

1. `useAppToasts`：边界最清晰，风险最低；
2. `useAppAuth`：与第 324 步 Auth API 接入直接相关；
3. `useWorkspaceNavigation`：隔离 active workspace 和 sidebar 逻辑；
4. 旧阶段 workspaces：拆分体量较大，放在前几个低风险 hook 之后。

风险提示：

旧 workspace orchestration 拆分比 `useAppToasts` / `useAppAuth` / `useWorkspaceNavigation` 风险更高。当前第一轮拆分已经覆盖 legacy idea/script、storyboard、image prompt、image generation。后续如果继续拆 system status、assets/tasks 展示或 remaining legacy UI，仍必须一次只拆一个小闭环，不要同时动 Auth、CreationHome、Document Round-trip、Usage Ledger 或后端；拆完必须运行 `npm run build` 和 `npm run test:e2e`。

## 7. 当前不做什么

当前不做：

- 不删除旧 storyboard / prompt / image 功能；
- 不迁移到 Redux / Zustand；
- 不引入 React Router 或其他路由库；
- 不新增依赖；
- 不改设计系统；
- 不做权限中间件；
- 不做生产部署；
- 不重写前端；
- 不一次性移动所有 workspaces；
- 不把 CreationHome 已拆出的结构重新塞回 `App.tsx`。

## 8. 验收标准

本文档合格标准：

- 明确 `App.tsx` 当前规模和风险；
- 明确不做大重构；
- 明确渐进拆分路线；
- 明确每步测试要求；
- 明确 Dramora 当前主线优先级；
- 不包含真实敏感信息；
- 不改代码。

当前结论：

前端 App 第一轮结构治理已完成。`App.tsx` 仍可继续优化，但已经从 2167 行下降到 1465 行，主要 workspace orchestration 已被拆出，不再是服务器部署前最大的结构阻塞项。当前服务器部署前的主要风险应转向 Auth 持久化、Usage Ledger 持久化、部署 Runbook、环境变量、HTTPS/CORS、日志脱敏和权限边界。后续可以继续渐进拆分，但不应继续为了“完美拆分”拖延部署前准备。
