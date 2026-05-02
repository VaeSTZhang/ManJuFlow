# ComfyUI Provider Technical Design｜真实 Provider 技术方案草案

## 1. 文档定位

本文档是未来真实 ComfyUI provider 的技术方案草案。

当前公开仓库只实现 mock provider 和 ComfyUI placeholder。当前不接真实 ComfyUI，不需要远端 GPU，也不购买服务器。真实 provider 只能在私有部署环境中实现和配置。

本文档只描述技术边界和后续实现方向，不包含真实服务器地址、API Key、SSH Key、真实 workflow、真实 workflow 文件名、模型权重路径或客户数据。

## 2. 当前已具备的基础

第四阶段当前已具备：

- ImageGeneration Schema 已完成；
- `/api/images/generate` 已完成；
- mock provider 已完成；
- ComfyUI placeholder 已完成；
- workflow registry 设计已完成；
- 私有部署 runbook 已完成；
- `.env.example` 已有安全占位变量。

这些能力已经可以支撑公开仓库中的 mock 闭环，也为后续私有环境中的真实 provider 实现提供接口基础。

## 3. 目标架构

未来真实 ComfyUI provider 的目标链路：

```text
Frontend
→ POST /api/images/generate
→ ImageGenerationService
→ get_image_generation_provider(provider)
→ ComfyUIImageGenerationProvider
→ private workflow registry
→ ComfyUI API
→ normalize result to ImageGenerationOutput
```

公开仓库不保存真实 registry。真实 workflow registry、workflow 文件、workflow id、模型配置、服务器配置和认证信息只存在于私有部署环境。

## 4. Provider 输入与输出

ComfyUI provider 输入应来自 `ImageGenerationInput`：

- `prompt_items`
- `workflow_name`
- `workflow_version`
- `workflow_preset`
- `extra_parameters`
- `provider = comfyui`

ComfyUI provider 输出必须归一化为 `ImageGenerationOutput`，其中每个 `ImageGenerationItem` 应包含：

- `task_id`
- `prompt_id`
- `shot_id`
- `image_url` / `local_path`
- `metadata`
- `error_message`

真实 provider 必须保持与 mock provider 一致的输出协议，让前端和上层 API 不需要关心底层是 mock 还是 ComfyUI。

## 5. 真实 ComfyUI provider 的核心职责

真实 ComfyUI provider 应负责：

- 读取私有环境配置；
- 解析 `workflow_name`；
- 从 workflow registry 获取私有 workflow；
- 合并 preset 和 request parameters；
- 构造 ComfyUI prompt graph / API payload；
- 提交任务；
- 轮询任务状态；
- 下载或记录输出资产；
- 转换为 `ImageGenerationOutput`；
- 做错误归一化；
- 不泄露敏感信息到日志。

provider 不应把真实 workflow、服务器地址、模型路径、客户素材或认证信息返回给前端。

## 6. 推荐模块边界

未来可拆分为以下模块，但当前不要创建这些文件：

`comfyui_client.py`

- `submit_prompt`
- `get_history`
- `get_result`
- `download_output` 或 `resolve_output_url`

`workflow_registry.py`

- `get_workflow_entry`
- `get_preset`
- `merge_parameters`

`image_generation_provider.py`

- `ComfyUIImageGenerationProvider`

`asset_manager.py` 或后续模块

- `save_image_asset`
- `build_public_or_private_asset_url`

拆分原则是让 ComfyUI API 通信、workflow 映射、provider 编排和资产存储彼此隔离，便于测试和私有部署替换。

## 7. 状态模型

ComfyUI 原始状态需要归一化为 ManJuFlow 状态：

- `pending`
- `running`
- `succeeded`
- `failed`
- `timeout`
- `cancelled`

当前 `ImageGenerationOutput.status` 可以先保持 `succeeded` / `failed`，后续再扩展任务状态中心、队列和资产管理。

## 8. 错误处理策略

真实 provider 应至少归一化以下错误：

- `workflow_not_found`
- `unsupported_preset`
- `comfyui_unreachable`
- `auth_failed`
- `timeout`
- `generation_failed`
- `invalid_output`
- `asset_save_failed`
- `provider_not_configured`

错误信息必须可读，但不应暴露 API Key、服务器地址、workflow 私有路径、模型路径、客户素材或私有对象存储信息。

## 9. 超时与重试策略

建议策略：

- 使用 `COMFYUI_TIMEOUT_SECONDS` 控制总等待时间；
- 使用 `COMFYUI_POLL_INTERVAL_SECONDS` 控制轮询间隔；
- 初期不做无限重试；
- 重试次数必须有限；
- 失败要返回可读 `error_message`；
- 避免重试风暴和成本失控。

真实图片生成涉及 GPU 成本。任何自动重试、批量任务或并发任务都应在成本控制方案明确后再开启。

## 10. 安全与日志策略

日志策略：

- 不打印 API Key；
- 不打印完整 workflow；
- 不打印客户素材；
- 不打印真实服务器地址；
- 只记录 `task_id`、`prompt_id`、`shot_id`、`provider`、`status`、耗时、错误类型；
- 私有配置不进入公开仓库。

如果需要排查私有环境问题，应在私有日志系统中处理，并确保日志脱敏。

## 11. 多 workflow 支持

结合 `docs/WORKFLOW_REGISTRY_DESIGN.md`，真实 provider 不应假设单一 workflow。

设计原则：

- `workflow_name` 是公开逻辑名；
- `private_workflow_ref` 只在私有 registry；
- provider 根据 `workflow_name` / `workflow_version` / `workflow_preset` 选择 workflow；
- 不同 workflow 可以有不同 `required_inputs` 和 `optional_inputs`。

公开仓库不提交真实 workflow registry，不提交真实 workflow 文件，也不提交私有 preset 内容。

## 12. 资产存储策略

未来真实图片输出可以：

- 保存在私有服务器目录；
- 上传到私有对象存储；
- 生成 `image_url`；
- 保存 `local_path`；
- 后续进入 asset manager。

当前公开仓库不实现真实资产存储。mock 阶段只返回占位 `mock_url` 和 `local_path`。

## 13. API 兼容策略

兼容原则：

- `/api/images/generate` 当前 mock contract 应尽量保持稳定；
- 真实 provider 应复用 `ImageGenerationInput` / `ImageGenerationOutput`；
- 前端不应该关心底层是 mock 还是 ComfyUI；
- provider 差异通过 `provider`、`workflow_name`、`metadata` 表达。

如果后续引入异步任务中心，应尽量保持当前同步 mock contract 可用于本地 demo 和测试。

## 14. 测试策略

未来应测试：

- mock provider 不受影响；
- comfyui provider 配置缺失时给出清晰错误；
- `workflow_not_found`；
- `unsupported_preset`；
- `timeout`；
- `invalid_output`；
- normalize result；
- 不依赖真实 ComfyUI 的单元测试；
- 私有环境单独跑集成测试。

公开仓库 CI / 本地测试应继续默认使用 mock，不依赖远端 GPU 或真实 ComfyUI。

## 15. 当前不做

当前明确不做：

- 不实现真实 provider；
- 不发 HTTP 请求；
- 不改代码；
- 不买服务器；
- 不上传 workflow；
- 不配置模型权重；
- 不做批量生产。

## 16. 进入真实联调前的条件

进入真实联调前应满足：

- 当前 mock 链路继续稳定；
- workflow registry 方案确认；
- 私有部署 runbook 确认；
- 安全 checklist 完成；
- 成本预算确认；
- 明确选择按量 GPU；
- 明确不会提交私有配置；
- 准备 1-2 条小样本 `prompt_items`。

任何一项未满足时，应继续停留在 mock provider 和文档设计阶段。

## 17. 后续步骤建议

建议后续步骤：

- 第 117 步：私有小样本联调 checklist；
- 第 118 步：更新 `PHASE_4_PROGRESS` / `README` 文档索引；
- 第 119 步：评估是否进入远端 GPU 准备；
- 如果暂不进入真实服务器，则继续 asset manager / task status mock。

下一步仍应优先完成 checklist 和边界确认，不应直接接真实服务器。
