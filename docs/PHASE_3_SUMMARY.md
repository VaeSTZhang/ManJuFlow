# ManJuFlow 第三阶段最终总结｜Storyboard → ImagePrompt

## 1. 阶段目标

第三阶段目标是将第二阶段产生的结构化分镜转换为 AI 绘图 Prompt：

```text
StoryboardOutput / 分镜文本
→ ImagePromptInput
→ ImagePromptOutput
→ 前端展示
→ 复制 / 导出绘图 Prompt JSON
```

该阶段为后续文生图、图生视频和视频化生产链路建立稳定的数据层和提示词层。第三阶段不直接生成图片或视频，而是先把“导演分镜”转成可校验、可复用、可追踪的 AI 绘图 Prompt。

## 2. 阶段完成概览

第三阶段已完成以下核心能力：

- `ImagePromptInput` / `ImagePromptItem` / `ImagePromptOutput` 数据协议；
- `storyboard_to_image_prompt_v1.md` 版本化 Prompt 模板；
- ImagePrompt mock service；
- ImagePrompt LLM parser；
- `POST /api/prompts/generate` 后端接口；
- `IMAGE_PROMPT_GENERATION_MODE=mock / llm` 模式切换；
- DeepSeek / Mimo / Kimi / MiniMax 四家文本 LLM provider 接入；
- 请求级 `llm_provider` / `llm_model` 选择；
- 前端“生成绘图 Prompt”区域；
- 前端 ImagePrompt 模型选择器；
- 绘图 Prompt JSON 展示、复制、导出；
- 分镜结果一键带入绘图 Prompt 生成；
- 前端完整链路“灵感 → 剧本 → 分镜 → 绘图 Prompt”浏览器验收；
- S001 四模型 ImagePrompt 第一轮对比；
- README 公开项目展示优化；
- 本地后端启动与端口清理脚本。

## 3. 后端成果

后端完成了第三阶段完整小闭环。

Schema：

- `apps/api/app/schemas/image_prompt.py`
- `ImagePromptInput`
- `ImagePromptItem`
- `ImagePromptOutput`
- `ImagePromptInput` 已支持请求级 `llm_provider` / `llm_model`

Prompt template：

- `apps/api/app/prompts/storyboard_to_image_prompt_v1.md`
- Prompt 负责将分镜转换为合法 `ImagePromptOutput` JSON
- Prompt 文件已版本化，后续可继续演进

Service：

- `apps/api/app/services/image_prompt_service.py`
- `generate_image_prompt_mock`
- `generate_image_prompt_llm`
- `generate_image_prompt`
- `load_image_prompt_template`

Parser：

- `parse_image_prompt_llm_response`
- 支持纯 JSON、Markdown code fence、JSON 前后少量解释文字
- 解析后通过 Pydantic 校验为 `ImagePromptOutput`
- 已接入 `clean_chinese_spacing`，用于清理真实模型输出中的中文异常空格

Endpoint：

- `apps/api/app/routers/prompts.py`
- `POST /api/prompts/generate`
- 请求体：`ImagePromptInput`
- 返回体：`ImagePromptOutput`

mock / llm 模式：

- `IMAGE_PROMPT_GENERATION_MODE=mock`
- `IMAGE_PROMPT_GENERATION_MODE=llm`
- mock 模式用于本地稳定开发和前端联调
- llm 模式用于真实模型小样本测试和模型对比

LLMClient 多 provider：

- DeepSeek
- Mimo / 小米大模型
- Kimi
- MiniMax

请求级 provider/model：

- `llm_provider`
- `llm_model`
- 不传时使用 `.env` 中默认 `LLM_PROVIDER`
- mock 模式下字段保留但不会触发真实 LLM 调用

provider-specific 参数：

- Kimi 已适配 `temperature=1.0`
- Kimi 已使用更长 timeout，避免偶发 `ReadTimeout`
- MiniMax 中国区 endpoint 已验证为 `https://api.minimaxi.com`

## 4. 前端成果

前端完成了第三阶段的可操作闭环。

- `apps/web/src/types/imagePrompt.ts` 已定义 ImagePrompt 类型；
- `apps/web/src/api/imagePrompts.ts` 已封装 `/api/prompts/generate`；
- 页面已新增“生成绘图 Prompt”区域；
- 支持输入项目标题、分镜摘要、分镜文本、目标模型、画面比例、风格预设、语言、额外要求；
- 支持模型选择器：
  - 使用后端默认
  - DeepSeek / deepseek-chat
  - Mimo / mimo-v2.5-pro
  - Kimi / kimi-k2.5
  - MiniMax / MiniMax-M2.7
- 支持当前模型显示；
- 明确提示：模型选择仅在后端 `IMAGE_PROMPT_GENERATION_MODE=llm` 时生效，mock 模式不消耗 API 额度；
- 支持 `ImagePromptOutput` 展示；
- 支持 `positive_prompt` / `negative_prompt` 展示；
- 支持绘图 Prompt JSON 复制；
- 支持绘图 Prompt JSON 导出；
- 支持分镜结果一键带入绘图 Prompt 生成。

浏览器验收结果：

- 绘图 Prompt 区域可以看到模型选择器；
- 默认可使用“后端默认”；
- 可以切换 DeepSeek / Mimo / Kimi / MiniMax；
- 当前模型显示正确；
- mock 模式下点击生成绘图 Prompt 不报错；
- 生成结果仍可展示、复制、导出；
- 页面整体运行正常。

## 5. 多模型接入成果

第三阶段已完成四家文本 LLM provider 的基础接入和小样本验证。

- DeepSeek：ImagePrompt 小样本通过；
- Mimo / 小米大模型：ImagePrompt 小样本通过；
- Kimi：ImagePrompt 小样本通过，已适配 `temperature=1.0` 和更长 timeout；
- MiniMax：ImagePrompt 小样本通过，当前中国区 endpoint 使用 `https://api.minimaxi.com`。

S001 第一轮对比：

- 样本：都市情感雨夜重逢；
- 四家 provider 均返回合法 `ImagePromptOutput`；
- 四家 provider 均返回 2 条 `ImagePromptItem`；
- 输出文件已保存到 `tests/fixtures/image_prompt_outputs/`；
- 结果已记录到 `docs/MODEL_COMPARISON_RESULTS.md`。

当前仍需继续补充：

- S002 悬疑反转办公室；
- S003 年代旧宅对峙；
- S004 多角色家庭冲突。

S002-S004 尚未完成，但不影响第三阶段核心能力收口。

## 6. 测试与质量保障

当前测试状态：

- 后端 `tests/api` 当前为 67 passed；
- 前端 `npm run build` 已通过；
- 前端浏览器验收已通过。

第三阶段测试覆盖包括：

- ImagePrompt Schema 测试；
- ImagePrompt service 测试；
- ImagePrompt LLM parser 测试；
- ImagePrompt endpoint 测试；
- LLM provider config 测试；
- 请求级 provider/model 覆盖测试；
- mock 模式隔离测试；
- 中文异常空格清洗测试。

质量原则：

- mock 先跑通，再接真实 LLM；
- 每个阶段保留 Schema / Prompt / Service / Endpoint / Frontend / Tests / Docs；
- 不提交真实 API Key；
- 不提交 `.env`；
- 公开仓库只保留可评审、可迁移、可复现的工程资产。

## 7. 文档与可交接成果

第三阶段已形成以下可交接文档：

- `README.md`
- `docs/API_CONTRACT.md`
- `docs/LOCAL_DEV.md`
- `docs/MVP_ROADMAP.md`
- `docs/PHASE_3_PROGRESS.md`
- `docs/PHASE_3_SUMMARY.md`
- `docs/MODEL_COMPARISON_PLAN.md`
- `docs/MODEL_COMPARISON_RESULTS.md`
- `docs/MODEL_COMPARISON_RUNBOOK.md`
- `docs/MODEL_COMPARISON_SAMPLES.md`
- `docs/LLM_TEST_LOG.md`

这些文档覆盖公开展示、API 契约、本地开发、阶段进展、模型对比、运行手册、真实 LLM 小样本记录和阶段总结。

## 8. 当前边界与未完成事项

以下内容尚未完成，属于后续规划或扩展：

- S002-S004 四模型 ImagePrompt 对比尚未完成；
- 自动模型评分系统尚未完成；
- 前端 UI 仍可继续美化；
- 尚未接入文生图；
- 尚未接入 ComfyUI；
- 尚未接入文生视频 / 图生视频；
- 尚未接入资产管理；
- 尚未接入任务队列；
- 尚未做生产部署；
- 尚未形成正式合作权属文件。

## 9. 对项目价值的意义

第三阶段让 ManJuFlow 从“文本生成 demo”升级为“面向 AI 视觉生产的结构化流水线底座”。

它解决了几个关键问题：

- 分镜和绘图 Prompt 之间有了稳定数据协议；
- 绘图 Prompt 可以被保存、复制、导出和后续复用；
- LLM 输出经过 parser 和 Schema 校验，不再只是不可控文本；
- 多模型 provider 可以在同一套链路下比较；
- 前端已具备模型选择入口；
- 后续接文生图 / 图生图 / 视频生成时，有明确的输入结构。

## 10. 对合作与投资评审的意义

当前项目已具备以下评审基础：

- 可运行 demo；
- 清晰工程结构；
- 明确的阶段划分；
- 多模型接入能力；
- 后端测试体系；
- 前端浏览器闭环；
- API 契约文档；
- 本地开发脚本；
- 公开仓库可评审；
- 后续迁移和定制基础。

该总结不包含任何具体合作方、个人身份、未公开谈判细节或真实 API Key。

## 11. 第四阶段建议

建议第四阶段围绕“ImagePrompt → ImageGeneration”展开。

优先建议：

- `ImageGenerationInput` / `ImageGenerationItem` / `ImageGenerationOutput` Schema；
- mock image generation endpoint；
- ComfyUI adapter 抽象；
- 远端 GPU / ComfyUI 私有部署方案；
- 前端图片生成展示；
- 图片结果复制 / 导出 / 下载；
- 图片生成任务状态基础设计。

公开仓库边界：

- 保留基础接口和可运行 mock 能力；
- 不提交真实服务器地址；
- 不提交 API Key；
- 不提交模型权重；
- 不提交客户数据；
- 不提交私有 ComfyUI workflow；
- 真实部署配置应放在私有部署环境。

## 12. 阶段结论

第三阶段已经达到高质量阶段性收口标准。

当前 ManJuFlow 已完成从灵感到剧本、分镜、绘图 Prompt 的前端和后端闭环，并具备多模型 provider 接入、请求级模型选择、结构化输出校验、模型对比样本、公开仓库文档和本地运行脚本。

第三阶段成果可以作为下一步合作沟通、投资评估和第四阶段开发的基础。
