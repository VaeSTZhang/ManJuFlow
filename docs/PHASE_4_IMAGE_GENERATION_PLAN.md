# Phase 4 Image Generation Plan｜文生图 / 远端 GPU / ComfyUI 方案

## 1. 阶段定位

第四阶段从第三阶段产出的 `ImagePromptOutput` 继续向 `ImageGenerationOutput` 推进，目标是建立“绘图 Prompt → 图片生成结果”的稳定工程边界。

本阶段优先建立以下能力：

- 文生图 / 图生图的公开仓库 mock 闭环；
- `ImageGeneration` 数据协议；
- `POST /api/images/generate` 后端接口；
- 前端 mock 图片结果展示；
- ComfyUI adapter 抽象；
- 后续远端 GPU 私有部署方案。

第四阶段不是马上接真实服务器，也不是马上把 ComfyUI 或 GPU 生产链路放入公开仓库。当前优先目标是先定义稳定接口、数据结构、mock 链路和安全边界，让后续真实部署可以在私有环境中替换 provider，而不破坏公开仓库的可评审性和可迁移性。

## 2. 当前项目已具备的前置能力

前三阶段已经完成 ManJuFlow 的核心文本与结构化创作链路：

- `IdeaInput` → `ScriptOutput`；
- `ScriptOutput` → `StoryboardOutput`；
- `StoryboardOutput` → `ImagePromptOutput`；
- mock / llm generation mode；
- 前端展示、复制、导出；
- 后端测试与文档；
- 多模型文本 LLM provider 接入。

当前项目已经具备稳定的 Schema / Prompt / Service / Endpoint / Frontend / Tests / Docs 分层方式。第四阶段应继续沿用该方式，把 ImageGeneration 作为下一个可测试、可展示、可替换的小闭环。

## 3. 第四阶段核心目标

第四阶段建议完成以下核心目标：

- 定义 `ImageGenerationInput` / `ImageGenerationItem` / `ImageGenerationOutput`；
- 新增 mock image generation service；
- 新增 `POST /api/images/generate`；
- 前端新增生成图片区域；
- 支持 `mock_url` / `image_url` 占位展示；
- 为 ComfyUI adapter 预留接口；
- 输出公开仓库可评审的文档和 runbook。

这些目标的重点是让公开仓库可以跑通本地 demo，验证数据协议、任务状态、前端展示和接口契约，而不是直接生产真实图片。

## 4. 第四阶段明确暂不做

第四阶段早期明确暂不做以下事项：

- 暂不提交真实服务器地址；
- 暂不提交 API Key；
- 暂不提交 SSH Key；
- 暂不提交真实 ComfyUI workflow；
- 暂不提交模型权重；
- 暂不提交客户数据；
- 暂不做批量生产任务；
- 暂不做文生视频；
- 暂不做 Redis / Celery / MinIO；
- 暂不做复杂任务队列；
- 暂不做生产部署。

本阶段所有公开仓库能力都应以 mock、本地演示、接口预留和文档边界为主。

## 5. 公开仓库边界

公开仓库可以包含：

- `ImageGeneration` Schema；
- mock endpoint；
- mock service；
- ComfyUI adapter interface / placeholder；
- `.env.example` 占位变量；
- 不含密钥的测试样例；
- docs / runbook；
- 本地可运行 demo。

公开仓库不能包含：

- 真实服务器 IP；
- SSH Key；
- API Key；
- `.env`；
- 模型权重；
- 私有 ComfyUI workflow；
- 客户数据；
- 合作方资料；
- 生产任务结果；
- 私有云存储配置。

公开仓库的定位是展示工程结构、接口契约、mock 闭环和可迁移方案，不承载真实生产环境配置。

## 6. 私有部署边界

未来进入真实部署时，远端 GPU / ComfyUI 应放在私有环境中管理。

建议边界如下：

- 远端 GPU / ComfyUI 放在私有环境；
- 真实 workflow 放私有仓库或服务器；
- 公开仓库只保留 adapter 抽象；
- 真实密钥走环境变量；
- 真实服务器信息只写在私有部署文档；
- 生成图片 / 视频资产进入私有对象存储或服务器存储；
- 公开仓库只保存 mock 样例。

公开仓库和私有部署环境之间应通过 provider interface、环境变量和私有 runbook 解耦，避免把客户资产、模型资产、服务器资产或 workflow 资产写入公开材料。

## 7. 建议的 ImageGeneration 数据协议初稿

以下字段为第四阶段数据协议初稿，后续会在 Schema 步骤中再正式落地。

### ImageGenerationInput

建议包含：

- `project_title`：项目标题；
- `prompt_items`：来自 `ImagePromptOutput.items` 的绘图 Prompt 条目；
- `provider`：图片生成 provider，例如 mock 或后续私有 ComfyUI provider；
- `workflow_name`：工作流名称或占位标识；
- `style_preset`：整体视觉风格；
- `aspect_ratio`：目标画面比例；
- `output_count`：每条 prompt 期望生成数量；
- `seed`：随机种子；
- `extra_parameters`：扩展参数。

### ImageGenerationItem

建议包含：

- `task_id`：生成任务 ID；
- `prompt_id`：对应的绘图 Prompt ID；
- `shot_id`：对应的分镜镜头 ID；
- `status`：任务状态，例如 pending / running / succeeded / failed；
- `positive_prompt`：正向 Prompt；
- `negative_prompt`：反向 Prompt；
- `provider`：图片生成 provider；
- `workflow_name`：工作流名称或占位标识；
- `image_url`：真实图片 URL；
- `mock_url`：mock 占位图片 URL；
- `local_path`：本地路径占位；
- `width`：图片宽度；
- `height`：图片高度；
- `seed`：实际使用的种子；
- `metadata`：生成元信息；
- `error_message`：失败原因。

### ImageGenerationOutput

建议包含：

- `project_title`：项目标题；
- `provider`：本次使用的图片生成 provider；
- `status`：整体状态；
- `items`：图片生成结果列表；
- `metadata`：整体元信息。

这些字段会在后续 Schema 步骤中结合 Pydantic 校验规则、默认值、字段约束和测试用例正式确定。

## 8. Mock Image Generation 策略

mock 阶段不生成真实图片。

建议策略：

- 根据 `prompt_id` / `shot_id` 返回稳定 `mock_url`；
- 使用占位图片路径或 placeholder URL；
- 保证前后端链路能展示图片卡片；
- 先验证数据协议、任务状态、前端展示；
- 不消耗 GPU 成本；
- 不暴露私有部署信息。

mock service 应保持确定性：相同输入在本地开发和 CI 中返回稳定结构，便于测试、截图验收和后续接口演进。

## 9. ComfyUI Adapter 抽象策略

后续 ComfyUI adapter 只负责抽象接口，不在公开仓库暴露真实 workflow。

建议设计为：

- `ImageGenerationProvider` interface；
- `MockImageGenerationProvider`；
- `ComfyUIImageGenerationProvider` placeholder；
- `submit_generation_task`；
- `poll_generation_task`；
- `normalize_generation_result`。

公开仓库可放 interface、placeholder、mock provider 和不含敏感信息的测试替身。真实 ComfyUI workflow、server_url、auth、模型路径应放在私有部署环境，通过环境变量、私有配置或私有 runbook 管理。

## 10. 多 workflow 设计预留

未来 ComfyUI workflow 不应假设只有一个。真实图片生产可能需要多个 workflow / preset / version，例如：

- `text_to_image_basic`
- `image_to_image_basic`
- `character_consistency`
- `scene_concept`
- `storyboard_preview`
- `upscale`
- `inpaint`
- `video_preprocess`

当前公开仓库不保存真实 workflow 文件，只保存公开安全的抽象字段和 mock 示例：

- `workflow_name`
- `workflow_version`
- `workflow_preset`
- `workflow_parameters`
- provider 抽象
- mock 示例

未来 `ImageGenerationInput` 中的 `workflow_name` 只是逻辑名称，不等同于真实私有 workflow 文件路径。真实 ComfyUI provider 应在私有环境中把逻辑 workflow 名称映射到私有 workflow 文件、workflow id、参数 preset 或版本配置。

公开仓库只描述多 workflow 设计边界，不提交真实 workflow registry、workflow 文件、模型路径或私有参数。

## 11. 远端 GPU / ComfyUI 私有部署策略

未来私有部署时应重点考虑：

- GPU 服务器访问控制；
- HTTPS / 内网访问；
- API token；
- 防止公网裸奔；
- 限流；
- 队列；
- 日志脱敏；
- 成本监控；
- 任务失败重试；
- 资产存储；
- 备份策略。

真实图片生成通常涉及较高成本、较大文件、较长任务时间和更复杂的失败状态。正式接入前应先在私有环境完成小样本联调，再决定是否引入队列、对象存储、任务表和生产监控。

## 12. 安全风险

第四阶段及后续真实部署至少存在以下风险：

| 风险 | 说明 | 缓解策略 |
| --- | --- | --- |
| API Key 泄露风险 | 真实 provider token 进入代码、文档、日志或截图 | 只使用环境变量和密钥管理；公开仓库只保留占位说明 |
| 服务器 IP 暴露风险 | 真实 GPU 服务器地址被提交到公开仓库 | 服务器信息只写入私有部署文档和私有配置 |
| workflow 泄露风险 | 私有 ComfyUI workflow 暴露模型组合、参数和业务流程 | 公开仓库只保留 adapter 抽象和 placeholder |
| 模型权重泄露风险 | 模型权重路径、文件或下载地址被公开 | 权重只保存在私有服务器或受控存储 |
| 客户素材泄露风险 | 客户图片、剧本、角色设定或生产结果进入公开样例 | 测试样例只使用虚构 mock 数据 |
| 生成内容合规风险 | 生成内容可能涉及版权、肖像、违规内容或平台审核风险 | 增加内容审核、提示词限制和人工复核流程 |
| 成本失控风险 | 批量任务、失败重试或公开接口滥用导致 GPU 成本飙升 | 私有环境加入认证、限流、配额、队列和成本监控 |

第四阶段公开仓库不应包含任何真实部署信息，以降低误提交和外部滥用风险。

## 13. 测试策略

第四阶段测试应覆盖：

- Schema 单元测试；
- mock service 单元测试；
- endpoint 测试；
- 前端 `npm run build`；
- 浏览器 mock 联调；
- 不依赖真实 GPU 的 CI / 本地测试；
- 私有环境单独联调 ComfyUI。

公开仓库测试应默认运行在 mock 模式，不依赖远端 GPU、真实 ComfyUI、真实 API Key、私有 workflow 或对象存储。真实 ComfyUI 联调应作为私有环境验收流程，不进入公开 CI。

## 14. 第四阶段建议步骤

建议以当前项目步数继续推进：

- 第 102 步：新增第四阶段方案文档；
- 第 103 步：定义 ImageGeneration Schema；
- 第 104 步：实现 mock image generation service；
- 第 105 步：新增 `POST /api/images/generate`；
- 第 106 步：补充后端测试；
- 第 107 步：前端新增 ImageGeneration 类型和 API；
- 第 108 步：前端新增生成图片 mock 区域；
- 第 109 步：浏览器 mock 联调；
- 第 110 步：更新 API_CONTRACT / LOCAL_DEV / MVP_ROADMAP；
- 第 111 步：设计 ComfyUI adapter interface；
- 第 112 步：新增私有部署 runbook 草案；
- 第 113 步：第四阶段中期总结。

每一步都应保持“小闭环、可测试、可回滚、无敏感信息”的推进原则。

## 15. 验收标准

第 102 步验收标准：

- `docs/PHASE_4_IMAGE_GENERATION_PLAN.md` 已新增；
- 文档明确公开仓库和私有部署边界；
- 文档明确暂不接真实服务器；
- 文档包含 ImageGeneration 数据协议初稿；
- 文档包含 mock、ComfyUI adapter、远端 GPU、安全、测试策略；
- 不修改代码；
- 不引入敏感信息。

本步骤完成后不进行 commit。

## 16. 当前完成进度

截至第 108 步，第四阶段已完成以下 mock 小闭环：

- 第 102 步：方案文档已完成；
- 第 103 步：ImageGeneration Schema 已完成；
- 第 104 步：mock image generation service 已完成；
- 第 105 步：`POST /api/images/generate` endpoint 已完成；
- 第 106 步：前端 ImageGeneration 类型和 API 封装已完成；
- 第 107 步：前端 Image Generation mock UI 已完成；
- 浏览器 mock 联调已通过；
- 手动 `prompt_items` JSON → `/api/images/generate` → mock 图片结果已通过；
- `ImagePromptResult` → `/api/images/generate` → mock 图片结果已通过；
- 当前仍未接真实 ComfyUI / GPU。

当前第四阶段已经具备公开仓库可评审的 ImagePrompt → ImageGeneration mock 闭环。后续重点是继续补全文档、设计 ComfyUI adapter interface，并将真实 ComfyUI workflow、服务器信息、密钥和资产存储严格留在私有部署环境。
