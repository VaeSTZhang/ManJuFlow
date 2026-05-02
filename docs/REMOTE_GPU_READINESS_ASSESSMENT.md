# Remote GPU Readiness Assessment｜远端 GPU 准备评估

## 1. 评估结论

当前不建议购买远端 GPU。

当前不建议安装真实 ComfyUI。

当前不建议进入真实图片生成联调。

当前应继续完善公开仓库中的 asset manager / task status mock / workflow registry mock 等基础能力。

## 2. 当前已经完成

第四阶段当前已经完成：

- ImageGeneration Schema；
- mock image generation service；
- `/api/images/generate`；
- 前端 Image Generation mock UI；
- provider interface；
- ComfyUI placeholder；
- workflow registry design；
- ComfyUI provider technical design；
- private deployment runbook；
- private integration checklist；
- README 主页优化；
- `docs/PHASE_4_PROGRESS.md`。

这些能力已经足够支撑公开仓库评审、本地 mock demo 和下一步架构设计。

## 3. 为什么现在还不买服务器

当前还不建议购买或租用远端 GPU，原因包括：

- 真实 provider 尚未实现；
- asset manager 尚未建立；
- task status / task center 尚未建立；
- 真实图片资产存储策略尚未落地；
- workflow registry 还只是设计文档；
- 成本控制和日志脱敏尚未工程化；
- 当前公开仓库 mock 链路仍可继续验证大部分产品流程；
- 过早接真实 GPU 会增加成本和安全风险。

在资产、任务状态、workflow registry mock 和错误归一化进一步稳定前，真实 GPU 联调的收益有限，成本和安全风险更高。

## 4. 进入远端 GPU 前还建议补齐什么

建议先补齐：

- `AssetItem` Schema；
- `RenderTask` / `ImageGenerationTask` 状态模型；
- asset manager mock；
- task status mock；
- workflow registry mock；
- provider config validation；
- 更完整的 error normalization；
- 私有联调 checklist 全部打勾；
- 至少 1 个端到端虚构样本稳定通过。

这些能力能让真实图片输出、长任务状态和多 workflow 接入有更稳定的承载层。

## 5. 推荐下一步路线

建议路线：

- 第 120 步：第四阶段阶段总结；
- 第 121 步：定义 `AssetItem` / `RenderTask` Schema；
- 第 122 步：实现 asset manager mock；
- 第 123 步：实现 task status mock；
- 第 124 步：前端展示生成资产 / task status；
- 第 125 步：再评估是否进入真实 ComfyUI 小样本联调。

如果不想拉长第四阶段，也可以先写 `PHASE_4_SUMMARY`，再新开第五阶段做 Asset / Task / Real ComfyUI Prep。

## 6. 购买服务器触发条件

只有以下条件满足，才建议购买或租用远端 GPU：

- Asset / Task mock 基础完成；
- workflow registry mock 完成；
- provider config validation 完成；
- checklist 全部满足；
- 已准备 1-2 条虚构 `prompt_items`；
- 已明确预算上限；
- 已确认只做按量计费；
- 已明确不会提交私有配置；
- 已明确失败停止条件。

任一条件不满足时，继续停留在 mock provider 阶段。

## 7. 服务器采购原则

只记录原则，不记录具体商家或账号信息：

- 初期只用按量；
- 不包月；
- 不长期租；
- 不直接上生产；
- 先小样本；
- 单次只生成 1 张图；
- 明确关机 / 停止计费流程；
- 记录成本和失败原因。

真正需要服务器时，再单独输出采购 / 租用建议。

## 8. 当前决策

本轮决策：暂不购买远端 GPU。

本轮决策：继续保持 mock provider。

本轮决策：先补齐 Asset / Task / Workflow Registry mock 或进入第四阶段总结。

## 9. 风险提示

如果现在强行接真实 GPU，可能导致：

- 成本失控；
- 没有 asset manager，图片结果难管理；
- 没有 task status，长任务体验不稳定；
- 没有 workflow registry mock，真实 workflow 多实例会返工；
- 密钥和服务器信息处理不当，影响公开仓库安全。

这些风险都可以通过继续完善 mock 架构和私有联调 checklist 来降低。

## 10. 后续记录

后续如果决策变化，需要更新：

- `docs/PHASE_4_PROGRESS.md`
- `docs/COMFYUI_PRIVATE_INTEGRATION_CHECKLIST.md`
- `docs/REMOTE_GPU_READINESS_ASSESSMENT.md`
- `README.md`

在这些文档更新前，不应把真实服务器、真实 workflow、密钥、模型权重或客户资产写入公开仓库。
