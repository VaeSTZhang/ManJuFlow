# Phase 4 Summary｜Image Generation / Asset / Task / Workspace 阶段总结

## 1. 阶段定位

第四阶段从 `ImagePromptOutput` 继续推进到 `ImageGenerationOutput`，并进一步补齐图片生成后需要的资产与任务承载层，包括 `AssetCollection`、`RenderTaskOutput`、`ImageGenerationBundleOutput` 和前端工作台能力。

本阶段定位是公开仓库安全的 mock / bundle 闭环：

- 当前不接真实 ComfyUI；
- 当前不需要远端 GPU；
- 当前不提交真实 workflow；
- 当前不提交真实服务器、密钥、模型权重或客户数据；
- 真实 provider、真实 workflow、真实资产存储和真实 GPU 联调留在私有部署环境。

第四阶段的核心价值不是提前生成真实图片，而是先建立可评审、可测试、可交接、可安全迁移到私有部署环境的数据协议、provider 抽象、mock endpoint、asset/task 承载和前端工作台闭环。

## 2. 阶段完成范围

后端：

- ImageGeneration Schema；
- mock image generation service；
- `POST /api/images/generate`；
- `ImageGenerationProvider` interface；
- `MockImageGenerationProvider`；
- `ComfyUIImageGenerationProviderPlaceholder`；
- `AssetItem` / `AssetCollection`；
- `RenderTaskItem` / `RenderTaskOutput`；
- asset manager mock service；
- render task mock service；
- `ImageGenerationBundleOutput`；
- image generation bundle service；
- `POST /api/images/generate-bundle`。

前端：

- ImageGeneration 类型和 API；
- Asset / RenderTask / Bundle 类型；
- `generateImageBundle` API；
- Image Generation mock UI；
- Bundle Summary；
- Assets 明细；
- Tasks 明细；
- AppShell + Sidebar 工作台布局；
- Sidebar workspace 切换；
- Toast Notification；
- 下一阶段自动跳转；
- ImagePrompt → ImageGeneration 自动跳转修复。

文档：

- `docs/PHASE_4_IMAGE_GENERATION_PLAN.md`；
- `docs/PHASE_4_PROGRESS.md`；
- `docs/WORKFLOW_REGISTRY_DESIGN.md`；
- `docs/COMFYUI_PROVIDER_TECHNICAL_DESIGN.md`；
- `docs/COMFYUI_PRIVATE_DEPLOYMENT_RUNBOOK_DRAFT.md`；
- `docs/COMFYUI_PRIVATE_INTEGRATION_CHECKLIST.md`；
- `docs/REMOTE_GPU_READINESS_ASSESSMENT.md`；
- `docs/FRONTEND_INFORMATION_ARCHITECTURE_PLAN.md`；
- `README.md` / `docs/LOCAL_DEV.md` / `docs/MVP_ROADMAP.md` 更新。

## 3. 当前完整链路

当前后端数据链路：

```text
IdeaInput
  -> ScriptOutput
  -> StoryboardOutput
  -> ImagePromptOutput
  -> ImageGenerationOutput
  -> ImageGenerationBundleOutput
  -> AssetCollection
  -> RenderTaskOutput
```

当前前端体验链路：

```text
Sidebar workspace
  -> 当前功能区
  -> 点击带入下一阶段
  -> 自动跳转下一 workspace
  -> Toast 提示
  -> ImageGeneration / Bundle / Assets / Tasks 展示
```

## 4. 当前 API

当前主要 API：

- `GET /health`
- `GET /api/system/status`
- `POST /api/scripts/generate`
- `POST /api/storyboards/generate`
- `POST /api/prompts/generate`
- `POST /api/images/generate`
- `POST /api/images/generate-bundle`

其中：

- `/api/images/generate` 返回 `ImageGenerationOutput`；
- `/api/images/generate-bundle` 返回组合结果，包含 `ImageGenerationOutput`、`AssetCollection` 和 `RenderTaskOutput`；
- 当前两个图片生成接口都只走 mock provider，不调用真实 ComfyUI / GPU。

## 5. 测试与验收结果

第四阶段最终验收结果：

- 后端 `python -m pytest tests/api`：185 passed；
- 前端 `npm run build`：通过；
- 浏览器主链路验收：通过；
- ImagePrompt → ImageGeneration mock / bundle 闭环：通过；
- Bundle Summary / Assets 明细 / Tasks 明细展示：通过；
- Sidebar workspace 切换：通过；
- Toast Notification：通过；
- 下一阶段自动跳转：通过。

后端日志确认以下接口均 `200 OK`：

- `/api/scripts/generate`
- `/api/storyboards/generate`
- `/api/prompts/generate`
- `/api/images/generate`
- `/api/images/generate-bundle`

## 6. 公开仓库安全边界

公开仓库可以包含：

- Schema；
- mock service；
- mock endpoint；
- provider interface；
- ComfyUI placeholder；
- mock assets / tasks；
- docs / runbook；
- safe examples；
- 本地 demo UI。

公开仓库不能包含：

- `.env`；
- API Key；
- SSH Key；
- 真实服务器地址；
- 真实 ComfyUI workflow；
- workflow registry 真实内容；
- 模型权重；
- 客户素材；
- 生产输出资产；
- 合作方敏感信息。

公开仓库只承载可评审架构、本地 mock demo、数据协议和安全集成边界。真实配置只进入私有部署环境。

## 7. 为什么第四阶段没有购买远端 GPU

第四阶段不建议购买远端 GPU，原因是：

- 当前 mock / bundle / asset / task / workspace 已能完成公开仓库评审目标；
- 真实 provider 尚不适合直接进入生产；
- 真实图片生成需要 asset manager、task center、workflow registry、成本控制和安全 checklist；
- 当前已通过 `docs/REMOTE_GPU_READINESS_ASSESSMENT.md` 明确暂不购买远端 GPU；
- 未来真正需要时，再按 `docs/COMFYUI_PRIVATE_INTEGRATION_CHECKLIST.md` 决策。

过早接入真实 GPU 会增加成本、安全和运维复杂度，也可能在 workflow registry、资产存储和任务状态模型尚未稳定时造成返工。

## 8. 资产保存策略

第四阶段确认的资产保存策略：

- 不无脑永久保存每一次生成的全部图片；
- 临时保存全部生成图用于预览、筛选、排查，可保留 1～7 天；
- 用户选中的图进入 Asset Manager 作为正式资产长期保存；
- 低质量、失败、废稿自动清理；
- 保留 metadata、prompt、seed、模型参数用于复现；
- 角色定稿图、场景定稿图、最终分镜图等重要版本做长期版本管理。

该策略用于避免资产无限增长、成本失控和素材管理混乱，也为后续真实 ComfyUI 输出接入 Asset Manager 做准备。

## 9. 第四阶段质量结论

第四阶段不是只做了 mock 图片，而是建立了：

- 数据协议；
- provider 抽象；
- mock endpoint；
- bundle endpoint；
- asset / task 承载；
- 前端工作台；
- Toast / workspace / auto navigation；
- 文档和安全边界；
- 全量测试验收。

第四阶段已经达到阶段性高质量收口标准：功能链路完整、公开仓库安全、测试通过、文档可交接，并且为后续私有 ComfyUI / 远端 GPU 联调保留了清晰边界。

## 10. 后续建议

第五阶段建议方向：

- Asset Manager 深化；
- Task Center / task status mock 深化；
- workflow registry mock；
- provider config validation；
- 真实 ComfyUI 小样本联调准备；
- 远端 GPU 按量评估；
- 图生视频 / 文生视频 adapter；
- UI 组件拆分与信息架构继续优化。

第五阶段开始前仍不建议直接购买服务器。只有在 checklist 满足，并且明确要做真实 ComfyUI 小样本联调时，才进入远端 GPU / ComfyUI 私有部署准备。

## 11. 交接备注

后续新对话或第五阶段开发应延续：

- 使用简体中文沟通；
- 每次一个小闭环；
- 质量优先，不跳步骤；
- 不提交敏感信息；
- 不写真实服务器、密钥、workflow、模型权重或客户数据；
- 需要重启前后端时明确说明；
- 保持公开仓库安全边界；
- 不直接接真实 GPU，除非用户明确进入私有联调；
- 若进入真实 ComfyUI 联调，必须先复核 private integration checklist。
