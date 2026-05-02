# ComfyUI Private Deployment Runbook Draft｜私有部署草案

## 1. 文档定位

本文档是未来真实 ComfyUI / 远端 GPU 联调前的私有部署准备草案。

当前公开仓库不包含真实部署配置，不包含真实服务器信息，不包含真实 ComfyUI workflow，不包含模型权重路径，也不包含任何客户数据。当前 ManJuFlow 第四阶段仍然使用 mock provider 完成 `ImageGenerationInput` → `ImageGenerationOutput` 的公开仓库闭环。

真实 ComfyUI 接入应发生在私有环境中。公开仓库只保留 provider 抽象、mock provider、ComfyUI placeholder、文档边界和不含敏感信息的测试样例。

## 2. 当前不需要购买服务器

当前阶段不需要购买远端 GPU。

当前阶段也不需要：

- 安装 ComfyUI；
- 上传模型权重；
- 准备真实 workflow；
- 配置真实服务器访问；
- 配置真实图片资产存储；
- 进行批量图片生成任务。

当前阶段只需要完成公开仓库 provider 抽象和 mock 链路，确保本地 demo、Schema、service、endpoint、前端 mock UI、测试和文档稳定。

## 3. 什么时候才需要准备远端 GPU

只有满足以下条件后，才建议准备远端 GPU / ComfyUI 私有联调：

- ImageGeneration mock 链路稳定；
- ComfyUI adapter interface 已完成；
- `API_CONTRACT` / `LOCAL_DEV` / `PHASE_4` 文档已更新；
- 私有部署 runbook 已完成；
- 准备做真实 ComfyUI 小样本联调；
- 已确认不会把真实配置提交到公开仓库。

在这些条件满足前，继续使用 mock provider 即可，不需要产生 GPU 成本。

## 4. 私有部署目标

未来真实私有部署应支持：

- 接收 `ImageGenerationInput`；
- 调用私有 ComfyUI workflow；
- 返回标准 `ImageGenerationOutput`；
- 保存真实图片资产；
- 保持 `prompt_id` / `shot_id` / `task_id` 可追踪；
- 不破坏公开仓库 mock 模式。

真实 provider 应遵循当前公开仓库的数据协议，让前端、测试和后续资产管理能力不依赖具体图片生成引擎。

## 5. 公开仓库与私有环境边界

公开仓库可以包含：

- provider interface；
- mock provider；
- ComfyUI placeholder；
- `.env.example` 占位变量；
- runbook 草案；
- mock 测试样例。

私有环境才包含：

- 真实服务器地址；
- 真实 API token；
- 真实 ComfyUI workflow；
- 真实模型权重；
- 真实输出图片；
- 客户素材；
- 私有对象存储配置。

任何真实服务器、密钥、workflow、模型权重、客户素材或生产输出，都不应进入公开仓库、公开文档、公开测试样例或公开日志。

## 6. 建议环境变量占位

未来可以在 `.env.example` 中保留以下占位变量名，但真实值只放私有 `.env`，不提交 Git：

- `COMFYUI_BASE_URL`
- `COMFYUI_API_TOKEN`
- `COMFYUI_WORKFLOW_NAME`
- `COMFYUI_TIMEOUT_SECONDS`
- `COMFYUI_POLL_INTERVAL_SECONDS`
- `COMFYUI_OUTPUT_BASE_URL`
- `IMAGE_GENERATION_PROVIDER`

说明：

- 公开仓库只写变量名和用途说明；
- `.env.example` 只保留占位变量和安全默认值；
- `IMAGE_GENERATION_PROVIDER=mock` 是公开仓库默认安全值；
- 私有 `.env` 保存真实值；
- `.env` 必须保持在 Git 忽略范围内；
- 不在代码、文档、测试、截图或日志中写入真实值。
- 切换到真实 provider 前，必须完成私有部署 checklist。

## 7. 最小私有联调流程草案

未来私有联调可按以下顺序准备，但本公开文档不记录任何真实 IP、真实 token、真实 workflow 或真实模型路径：

1. 准备远端 GPU 机器。
2. 安装 ComfyUI。
3. 上传或配置私有 workflow。
4. 配置模型权重。
5. 配置访问认证。
6. 在私有 `.env` 中配置 provider。
7. 启动 ManJuFlow API。
8. 用一个 `prompt_items` 小样本调用 `/api/images/generate`。
9. 检查 `ImageGenerationOutput`。
10. 检查图片资产存储。
11. 检查日志不泄露敏感信息。

初次联调只建议使用单条 prompt、单张输出和可控样本，避免直接进入批量生产。

## 8. 安全 checklist

私有部署前必须检查：

- 不允许公网裸奔；
- 必须有访问控制；
- 不提交 `.env`；
- 不提交 workflow；
- 不提交模型权重；
- 不提交输出图片；
- 不把客户素材放公开样例；
- 日志脱敏；
- 限流；
- 成本监控；
- 失败重试限制；
- 关闭不必要端口。

如果任何一项无法满足，应暂停真实 ComfyUI 联调，继续使用 mock provider。

## 9. 成本控制建议

初期建议只使用按量计费或等价的可控成本方案。

成本控制原则：

- 先做小样本；
- 不做批量任务；
- `output_count` 控制在 1；
- 不开自动重试风暴；
- 每次联调记录耗时、成本、失败原因。

在真实 provider、队列、重试和资产存储策略稳定前，不建议开放批量生产能力。

## 10. 与当前代码的关系

当前代码状态：

- `/api/images/generate` 已存在；
- mock provider 已存在；
- ComfyUI placeholder 已存在；
- 真实 ComfyUI provider 尚未实现；
- 后续会在私有环境中实现真实 provider。

当前公开仓库的默认行为仍然是 mock image generation。ComfyUI placeholder 只用于表达扩展边界，调用时应明确失败，不会发起真实 HTTP 请求，也不会读取真实私有配置。

## 11. 后续实施建议

建议后续顺序：

- 第 111 步：更新 PHASE_4 文档，记录 provider interface 和 runbook；
- 第 112 步：补充 `.env.example` 的 ComfyUI 占位变量；
- 第 113 步：设计真实 ComfyUI provider 的技术方案，但不写真实配置；
- 第 114 步：准备私有小样本联调 checklist；
- 真正需要服务器时再单独决策。

在进入真实联调前，继续保持公开仓库和私有部署环境隔离。
