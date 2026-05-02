# Phase 4 Progress｜Image Generation / ComfyUI Mock 阶段进度

## 1. 阶段目标

第四阶段目标是从 `ImagePromptOutput` 推进到 `ImageGenerationOutput`，先建立公开仓库安全的 mock 闭环，再设计 ComfyUI provider 抽象和私有部署边界。

当前阶段重点是：

- 建立 `ImageGeneration` 数据协议；
- 跑通 `ImagePromptOutput.items` → `/api/images/generate` → `ImageGenerationOutput`；
- 在前端展示 mock image card；
- 为后续真实 ComfyUI / 远端 GPU 接入预留 provider 抽象；
- 明确公开仓库与私有部署环境边界。

当前不接真实 ComfyUI，不需要远端 GPU，不提交真实 workflow，不提交模型权重路径，不提交服务器信息，也不提交客户数据。当前公开仓库以 mock、本地 demo、接口契约、provider 抽象和文档边界为主。

## 2. 已完成步骤总览

- 第 102 步：新增 `docs/PHASE_4_IMAGE_GENERATION_PLAN.md`；
- 第 103 步：新增 ImageGeneration Schema；
- 第 104 步：新增 mock image generation service；
- 第 105 步：新增 `POST /api/images/generate`；
- 第 106 步：新增前端 ImageGeneration 类型和 API 封装；
- 第 107 步：新增前端 Image Generation mock UI；
- 第 108 步：更新 Image Generation mock 文档；
- 第 109 步：新增 image generation provider interface；
- 第 110 步：新增 ComfyUI 私有部署 runbook 草案；
- 第 111 步：补充 `.env.example` 的 ImageGeneration / ComfyUI 占位变量；
- 第 112 步：补充多 workflow / workflow registry 设计说明；
- 第 113 步：优化 GitHub README 项目主页展示。

## 3. 当前已完成的技术能力

后端：

- `ImageGenerationPromptItem`
- `ImageGenerationInput`
- `ImageGenerationItem`
- `ImageGenerationOutput`
- `generate_image_generation_mock`
- `generate_image_generation`
- `ImageGenerationProvider`
- `MockImageGenerationProvider`
- `ComfyUIImageGenerationProviderPlaceholder`
- `get_image_generation_provider`
- `POST /api/images/generate`

前端：

- `apps/web/src/types/imageGeneration.ts`
- `apps/web/src/api/imageGenerations.ts`
- Image Generation mock UI
- 手动 `prompt_items` JSON 测试
- 从 `ImagePromptResult` 带入生成 mock 图片

文档：

- `docs/PHASE_4_IMAGE_GENERATION_PLAN.md`
- `docs/COMFYUI_PRIVATE_DEPLOYMENT_RUNBOOK_DRAFT.md`
- `docs/API_CONTRACT.md`
- `docs/LOCAL_DEV.md`
- `docs/MVP_ROADMAP.md`
- `README.md`

## 4. 当前测试状态

当前已知测试状态：

- `python -m pytest tests/api` 已通过，当前为 113 passed；
- ImageGeneration 相关 schema / service / endpoint / provider 测试均已通过；
- 前端 `npm run build` 已通过；
- 浏览器 mock 联调已通过；
- `/api/images/generate` mock curl 测试已通过；
- `ImagePromptResult` → `/api/images/generate` → mock image card 已通过。

说明：截至第 109 步后端 `tests/api` 为 113 passed。后续如果继续新增测试，应同步更新本文档或阶段总结。

## 5. 当前公开仓库安全边界

公开仓库可以包含：

- Schema；
- mock service；
- mock endpoint；
- provider interface；
- ComfyUI placeholder；
- `.env.example` 占位变量；
- docs / runbook；
- safe mock examples。

公开仓库不能包含：

- API Key；
- `.env`；
- SSH Key；
- 真实服务器地址；
- 真实 ComfyUI workflow；
- workflow registry 真实内容；
- 模型权重；
- 客户数据；
- 合作方敏感资料；
- 生产输出资产。

公开仓库的价值是可评审架构、本地 mock demo、数据协议和安全集成边界，不承载真实生产部署资产。

## 6. 多 workflow 设计记录

用户已明确提醒：未来 ComfyUI workflow 不止一个。

后续设计必须预留：

- `workflow_name`
- `workflow_version`
- `workflow_preset`
- `workflow_parameters`
- workflow registry / workflow mapping
- provider adapter normalization

`COMFYUI_WORKFLOW_NAME` 目前只是默认占位变量，不代表系统只能支持一个 workflow。真实私有部署应通过 workflow registry 或 workflow mapping，把公开数据协议中的逻辑名称映射到私有 workflow 文件、workflow id、参数 preset 或版本配置。

公开仓库不提交真实 workflow registry、不提交真实 workflow 文件、不提交模型路径、不提交私有参数。

## 7. 远端 GPU / ComfyUI 采购时机

当前不需要购买远端服务器。

当前也不需要：

- 安装 ComfyUI；
- 准备模型权重；
- 准备真实 workflow；
- 配置真实服务器；
- 配置真实对象存储；
- 做批量图片生产任务。

只有在以下条件满足后，才考虑远端 GPU：

- mock 链路稳定；
- provider interface 稳定；
- runbook 完成；
- `.env.example` 占位完成；
- workflow registry 设计明确；
- 准备做真实 ComfyUI 小样本联调；
- 已确认不会把真实配置提交公开仓库。

## 8. 下一步建议

建议后续步骤：

- 第 115 步：补充真实 ComfyUI provider 技术方案文档，但不写真实配置；
- 第 116 步：设计 workflow registry / preset mapping 文档；
- 第 117 步：整理私有小样本联调 checklist；
- 第 118 步：评估是否需要进入真实远端 GPU 准备；
- 第 119 步：如仍不买服务器，则继续做 asset manager / task status mock；
- 第 120 步：第四阶段阶段总结。

下一阶段仍不建议直接接真实服务器。应先把真实 provider 技术方案、workflow registry、私有联调 checklist 和安全边界写清楚。

## 9. 质量原则

第四阶段继续保持前三阶段同等质量：

- 不为了快提前接真实 ComfyUI；
- 每一步小闭环都应有测试、文档和 commit；
- 避免后期反复缝缝补补；
- 继续保持 Schema / Service / Provider / Endpoint / Frontend / Tests / Docs 分层；
- 保持公开仓库可评审、可迁移、可交接；
- 真实密钥、服务器、workflow、模型权重和客户资产只进入私有部署环境。
