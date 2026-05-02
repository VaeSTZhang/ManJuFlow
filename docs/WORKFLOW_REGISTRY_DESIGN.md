# Workflow Registry Design｜多 Workflow / Preset 映射设计

## 1. 设计背景

第四阶段已经完成 `ImagePromptOutput` → `ImageGenerationOutput` 的 mock 闭环。

后续如果接入真实 ComfyUI，不能假设只有一个 workflow。不同生产任务会需要不同 workflow、不同参数、不同控制条件和不同输出策略。

公开仓库只保存抽象设计，不保存真实 workflow、不保存真实 workflow 文件名、不保存模型权重路径、不保存服务器信息，也不保存客户数据。

## 2. 为什么不能只用一个 COMFYUI_WORKFLOW_NAME

单一 `COMFYUI_WORKFLOW_NAME` 只能作为默认占位，不能作为长期架构假设。

风险包括：

- 文生图、图生图、角色一致性、局部重绘、高清修复、视频预处理需求不同；
- 不同 workflow 输入参数不同；
- 不同模型、采样器、尺寸、控制条件不同；
- 后期新增 workflow 会导致代码返工；
- 公开逻辑名不应暴露私有 workflow 文件。

因此，`workflow_name` 应被视为公开逻辑名称，而不是私有 workflow 文件路径。

## 3. 核心概念

- `provider`：图片生成 provider，例如 `mock`、`comfyui` 或未来其他 provider。
- `workflow_name`：公开逻辑名称，用于表达业务意图，不是私有文件路径。
- `workflow_version`：workflow 版本，用于区分同一逻辑名称下的不同实现。
- `workflow_preset`：一组预设参数，不一定等于完整 workflow。
- `workflow_parameters`：单次请求的 workflow 参数覆盖。
- `workflow_registry`：私有环境中的 workflow 映射表。
- `workflow_mapping`：逻辑 workflow 到私有 workflow 引用、版本和 preset 的映射关系。
- `normalized_input`：provider 接收到的标准化输入。
- `normalized_output`：provider 返回的标准化输出，对齐 `ImageGenerationOutput`。

`workflow_registry` 应存在于私有环境。公开仓库只记录设计边界和 mock 示例。

## 4. 建议的 workflow 类型

未来可能支持的 workflow 类型包括：

- `text_to_image_basic`
- `image_to_image_basic`
- `character_consistency`
- `scene_concept`
- `storyboard_preview`
- `upscale`
- `inpaint`
- `video_preprocess`
- `style_transfer`
- `reference_pose`
- `reference_face`
- `background_generation`

当前公开仓库不实现这些真实 workflow，只做预留。

## 5. 建议数据结构草案

以下只是设计草案，不是当前代码实现。

`WorkflowRegistryEntry` 可包含：

- `workflow_name`
- `workflow_version`
- `provider`
- `task_type`
- `description`
- `private_workflow_ref`
- `default_preset`
- `supported_presets`
- `required_inputs`
- `optional_inputs`
- `output_type`
- `safety_notes`

`WorkflowPreset` 可包含：

- `preset_name`
- `description`
- `aspect_ratio`
- `width`
- `height`
- `steps`
- `cfg_scale`
- `sampler`
- `scheduler`
- `model_hint`
- `control_modules`
- `extra_parameters`

`private_workflow_ref` 只能存在于私有配置，不进入公开仓库。

## 6. ImageGenerationInput 如何使用 workflow

后续 `ImageGenerationInput` 可以逐步扩展，也可以先保持兼容。

建议字段方向：

- `workflow_name`：公开逻辑名称；
- `workflow_version`：可选版本；
- `workflow_preset`：可选预设；
- `extra_parameters`：业务扩展参数；
- `provider`：`mock` / `comfyui` / future provider。

当前已存在 `workflow_name`，可先作为最小入口，不急于马上改 Schema。

## 7. Provider 如何解析 workflow

未来真实 ComfyUI provider 的逻辑可以是：

1. 接收 `ImageGenerationInput`。
2. 读取 `workflow_name` / `workflow_version` / `workflow_preset`。
3. 在私有 workflow registry 中查找对应 workflow。
4. 合并默认 preset 和请求参数。
5. 构造 ComfyUI API 请求。
6. 提交任务。
7. 轮询结果。
8. 归一化为 `ImageGenerationOutput`。

公开仓库 provider 只保留 mock provider 和 ComfyUI placeholder。真实请求构造、认证、workflow 加载和资产存储应放在私有部署环境。

## 8. 公开仓库与私有 registry 边界

公开仓库可以包含：

- registry schema draft；
- mock registry examples；
- logical workflow names；
- docs；
- tests with fake workflow names。

私有环境才包含：

- `private_workflow_ref`；
- 真实 workflow 文件；
- workflow id；
- 模型路径；
- ControlNet / LoRA / checkpoint 配置；
- 私有参数；
- 存储路径；
- 真实输出资产。

## 9. Mock registry 策略

公开仓库未来可以有 mock registry。

mock registry 原则：

- 只使用 fake workflow names；
- 不映射真实 workflow 文件；
- 用于测试 provider 选择和 UI 预设选择；
- 不调用真实 ComfyUI；
- 不包含模型路径、服务器地址或私有参数。

mock registry 的价值是验证接口和选择逻辑，不代表真实生产配置。

## 10. 前端未来如何使用

未来前端可以：

- 显示 workflow 类型选择；
- 显示 preset 选择；
- 根据 `workflow_name` 切换参数表单；
- 保持非技术用户易用；
- 不暴露私有 workflow 文件名；
- 只展示业务友好的名称，例如“竖屏短剧写实图”“角色一致性图”“场景概念图”。

前端展示的是业务概念，不是 ComfyUI 内部文件名、节点图结构或私有模型配置。

## 11. 测试策略

未来测试应覆盖：

- registry entry schema；
- preset mapping；
- unknown workflow；
- unsupported preset；
- provider fallback；
- mock workflow generation；
- 不依赖真实 ComfyUI。

公开仓库测试应使用 fake workflow names 和 mock provider，不依赖远端 GPU、真实 workflow、真实模型权重或私有对象存储。

## 12. 当前不做

当前明确不做：

- 不实现真实 workflow registry；
- 不提交真实 workflow；
- 不修改 Schema；
- 不修改 provider；
- 不接真实 ComfyUI；
- 不买服务器。

## 13. 后续步骤建议

建议后续步骤：

- 第 116 步：真实 ComfyUI provider 技术方案文档；
- 第 117 步：私有小样本联调 checklist；
- 第 118 步：评估是否需要远端 GPU；
- 第 119 步：如暂不接真实服务器，继续 asset manager / task status mock。

在真实 ComfyUI 联调前，应先完成私有 registry 方案、安全 checklist 和成本控制策略。
