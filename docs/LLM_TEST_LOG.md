# ManJuFlow 真实 LLM 调用测试记录

## Dramora generate-from-source LLM Path Check - 2026-05-04

### 检查目标

确认 `POST /api/scripts/generate-from-source` 在 `SCRIPT_GENERATION_MODE=llm` 时，是否真正进入 DeepSeek / LLMClient 生成链路，还是仍然只返回 mock 输出。

### 调用链

第 221 步检查时的静态调用链：

```text
POST /api/scripts/generate-from-source
-> apps/api/app/routers/scripts.py
-> generate_short_drama_script_mock(input_data)
-> apps/api/app/services/script_generation/generator.py
-> idea: generate_script_mock(...)
-> film_script: generate_film_script_adaptation_mock(...)
-> novel: generate_novel_adaptation_mock(...)
```

对照旧入口：

```text
POST /api/scripts/generate
-> generate_script(input_data)
-> 读取 get_settings().script_generation_mode
-> mock: generate_script_mock(...)
-> llm: generate_script_with_llm(...)
-> LLMClient().chat(...)
-> ScriptOutput.model_validate(...)
```

### 当前结论

B. 只具备 mock path，尚未实现真实 LLM path。

第 221 步检查时，`/api/scripts/generate-from-source` 没有读取 `SCRIPT_GENERATION_MODE`，没有分 `mock` / `llm`，没有调用 `LLMClient`，也没有把真实 LLM 输出解析为 `ShortDramaScriptOutput`。

第 222 步更新：

- 已新增统一入口 `generate_short_drama_script(input_data)`；
- `/api/scripts/generate-from-source` 已改为调用统一入口；
- `SCRIPT_GENERATION_MODE=mock` 仍复用现有 mock 链路；
- `SCRIPT_GENERATION_MODE=llm` 已被识别，但暂时返回清晰未实现错误；
- 当前仍未调用真实 LLM，下一步将实现 `source_mode=idea` 的真实 LLM path。

第 223 步更新：

- 已为 `source_mode=idea` 增加 `SCRIPT_GENERATION_MODE=llm` path；
- idea llm path 复用既有 `idea_to_script_v1.md`、`generate_script_with_llm`、`ScriptOutput` 解析能力；
- `ScriptOutput` 已转换为 `ShortDramaScriptOutput`；
- `ai_options.provider` / `ai_options.model` 已传入 `LLMClient(provider=..., model=...)`；
- metadata 会记录 `generation_mode=llm`、source_mode、provider、model、purpose；
- `film_script` / `novel` 的 llm path 尚未实现，仍返回清晰未实现错误；
- 本步骤单元测试使用 fake LLM，未调用真实 DeepSeek；下一步可以进行 idea + DeepSeek 虚构样本真实 smoke test。

第 229 步更新：

- 已为 `source_mode=film_script` 增加 `SCRIPT_GENERATION_MODE=llm` path；
- film_script llm path 复用 `film_script_to_short_drama_v1.md` Prompt，并直接校验为 `ShortDramaScriptOutput`；
- `ai_options.provider` / `ai_options.model` 已传入 `LLMClient(provider=..., model=...)`；
- metadata 会记录 `generation_mode=llm`、source_mode、provider、model、purpose；
- 当前只完成代码路径与 fake LLM 测试，尚未进行真实 DeepSeek film_script 样本；
- `novel` 的 llm path 尚未实现，仍返回清晰未实现错误；
- 下一步建议做 film_script + DeepSeek 虚构样本验收。

第 231 步更新：

- 已为 `source_mode=novel` 增加 `SCRIPT_GENERATION_MODE=llm` path；
- novel llm path 复用 `novel_to_short_drama_v1.md` Prompt，并直接校验为 `ShortDramaScriptOutput`；
- `ai_options.provider` / `ai_options.model` 已传入 `LLMClient(provider=..., model=...)`；
- metadata 会记录 `generation_mode=llm`、source_mode、provider、model、purpose；
- metadata 额外记录 `prompt_template_name=novel_to_short_drama_v1.md` 与 `context_policy=current_project_only`；
- 当前只完成代码路径与 fake LLM 测试，尚未进行真实 DeepSeek novel 样本；
- idea / film_script 已完成真实 DeepSeek 小样本；
- 下一步建议做 novel + DeepSeek 虚构样本验收。

### 是否真实调用 DeepSeek

否。

第 221 步没有启动后端真实调用，也没有执行 DeepSeek curl。原因是当时代码路径尚未具备真实 LLM 分支，直接调用会继续返回 mock 结果，无法证明 DeepSeek 剧本生成链路已跑通。

### ai_options 是否已进入请求

已进入请求 schema。

`ShortDramaGenerationInput.ai_options` 已支持 provider / model / language / purpose，mock metadata 也会记录这些字段。第 223 步后，idea llm path 已会把 provider / model 传入 `LLMClient`；第 229 步后，film_script llm path 也已接入 provider / model；第 231 步后，novel llm path 也已接入 provider / model。

### 阻塞点

- 第 221 步检查时，`generate-from-source` router 直接调用 `generate_short_drama_script_mock`；
- 第 222 步已新增统一 `generate_short_drama_script` 入口，并开始读取 `SCRIPT_GENERATION_MODE`；
- idea source_mode 已具备真实 LLM prompt 组装、调用、JSON 解析、清洗和 `ShortDramaScriptOutput` 转换闭环；
- film_script source_mode 已具备真实 LLM prompt 组装、调用、JSON 解析、清洗和 `ShortDramaScriptOutput` 校验闭环；
- novel source_mode 已具备真实 LLM prompt 组装、调用、JSON 解析、清洗和 `ShortDramaScriptOutput` 校验闭环，但尚未进行真实 DeepSeek smoke test。

### 下一步建议

- 第 222 步已完成统一入口 `generate_short_drama_script(input_data)`；
- 第 222 步已在该入口读取 `SCRIPT_GENERATION_MODE`；
- `mock` 分支继续复用现有 `generate_short_drama_script_mock`；
- 第 223 步已实现 idea llm 分支，并调用 `LLMClient(provider=input_data.ai_options.provider, model=input_data.ai_options.model)`；
- 第 223 步已将 idea 真实模型输出转换为 `ShortDramaScriptOutput`，并复用 metadata helper 记录 provider / model / purpose；
- 下一步执行 DeepSeek 小样本 smoke test；
- 第 229 步已实现 film_script llm 分支，但尚未做真实 DeepSeek film_script 样本；
- 下一步执行 film_script DeepSeek 虚构样本 smoke test；
- 第 231 步已实现 novel llm 分支，但尚未做真实 DeepSeek novel 样本；
- 下一步执行 novel DeepSeek 虚构样本 smoke test。

安全记录：

- 不记录 API Key；
- 不记录 `.env` 内容；
- 不使用真实客户内容；
- 本次只做静态路径审计和后端测试。

## Dramora Idea Script Generation DeepSeek Smoke Test - 2026-05-04

### 测试目标

验证 Dramora 三入口剧本生成链路中 `source_mode=idea` 的真实 DeepSeek 调用是否可用，并确认返回结果能够承载为 `ShortDramaScriptOutput`。

### 测试接口

- Endpoint：`POST /api/scripts/generate-from-source`
- `SCRIPT_GENERATION_MODE`：`llm`

### source_mode

- `source_mode`：`idea`

### provider / model / purpose

- provider：`deepseek`
- model：`deepseek-chat`
- purpose：`script_generation`

### 是否真实 llm 模式

是。

本次使用 `SCRIPT_GENERATION_MODE=llm`，并通过请求级 `ai_options` 指定 DeepSeek provider / model。

### 虚构样本说明

测试使用虚构短剧样本，不使用真实客户剧本，不使用真实公司项目文本，不记录完整生成内容作为客户数据。

### 返回结构检查结果

返回结果包含 `ShortDramaScriptOutput` 关键字段：

- `project_title`
- `logline`
- `world_setting`
- `characters`
- `episodes`
- `metadata`

### metadata 检查结果

返回 metadata 已包含本次生成追踪字段：

- `metadata.generation_mode = llm`
- `metadata.provider = deepseek`
- `metadata.model = deepseek-chat`
- `metadata.purpose = script_generation`

### 安全说明

- 未打印 API Key；
- 未提交 `.env`；
- `.env` 未被 Git 跟踪；
- 未使用真实客户剧本；
- 测试样本为虚构内容。

### 后续限制

- 当前只验证 `source_mode=idea`；
- `film_script` / `novel` 的 llm path 仍未实现；
- 下一步建议做前端 idea 入口真实 llm 浏览器验收；
- 之后再分步接入 `film_script` / `novel` 的真实 llm path。

## Dramora Film Script DeepSeek Smoke Test - 2026-05-04

### 测试目标

验证 Dramora 三入口剧本生成链路中 `source_mode=film_script` 的真实 DeepSeek 调用是否可用，并确认返回结果能够承载为 `ShortDramaScriptOutput`。

### 测试接口

- Endpoint：`POST /api/scripts/generate-from-source`
- `SCRIPT_GENERATION_MODE`：`llm`

### source_mode

- `source_mode`：`film_script`

### provider / model / purpose

- provider：`deepseek`
- model：`deepseek-chat`
- purpose：`film_adaptation`

### 是否真实 llm 模式

是。

本次使用 `SCRIPT_GENERATION_MODE=llm`，并通过请求级 `ai_options` 指定 DeepSeek provider / model。

### 虚构样本说明

测试使用虚构电影剧本片段，不使用真实客户剧本，不使用真实公司项目文本，不记录完整生成内容作为客户数据。

### 返回结构检查结果

返回结果包含 `ShortDramaScriptOutput` 关键字段：

- `project_title`
- `logline`
- `world_setting`
- `characters`
- `adaptation_notes`
- `episodes`
- `metadata`

### metadata 检查结果

返回 metadata 已包含本次生成追踪字段：

- `metadata.generation_mode = llm`
- `metadata.provider = deepseek`
- `metadata.model = deepseek-chat`
- `metadata.purpose = film_adaptation`

### 安全说明

- 未打印 API Key；
- 未提交 `.env`；
- `.env` 未被 Git 跟踪；
- 未使用真实客户剧本；
- 测试样本为虚构电影剧本片段。

### 后续限制

- 当前已验证 `source_mode=idea`；
- 当前已验证 `source_mode=film_script`；
- `novel` 的 llm path 仍未实现。

## Dramora Novel DeepSeek Smoke Test - 2026-05-04

### 测试目标

验证 Dramora 三入口剧本生成链路中 `source_mode=novel` 的真实 DeepSeek 调用是否可用，并确认返回结果能够承载为 `ShortDramaScriptOutput`。

### 测试接口

- Endpoint：`POST /api/scripts/generate-from-source`
- `SCRIPT_GENERATION_MODE`：`llm`

### source_mode

- `source_mode`：`novel`

### provider / model / purpose

- provider：`deepseek`
- model：`deepseek-chat`
- purpose：`novel_adaptation`

### 是否真实 llm 模式

是。

本次使用 `SCRIPT_GENERATION_MODE=llm`，并通过请求级 `ai_options` 指定 DeepSeek provider / model。

### 虚构样本说明

测试使用虚构小说片段，不使用真实小说，不使用真实客户剧本，不记录完整生成内容作为客户数据。

### 返回结构检查结果

返回结果包含 `ShortDramaScriptOutput` 关键字段：

- `project_title`
- `logline`
- `world_setting`
- `characters`
- `adaptation_notes`
- `episodes`
- `metadata`

### metadata 检查结果

返回 metadata 已包含本次生成追踪字段：

- `metadata.generation_mode = llm`
- `metadata.provider = deepseek`
- `metadata.model = deepseek-chat`
- `metadata.purpose = novel_adaptation`
- `metadata.prompt_template_name = novel_to_short_drama_v1.md`

### 安全说明

- 未打印 API Key；
- 未提交 `.env`；
- `.env` 未被 Git 跟踪；
- 未使用真实小说或真实客户剧本；
- 测试样本为虚构小说片段。

### 阶段结论

- idea / film_script / novel 三入口均已完成 DeepSeek 小样本；
- 下一步建议进行前端三入口真实 LLM 浏览器验收。

## Dramora Frontend Idea DeepSeek Browser Acceptance - 2026-05-04

### 验收目标

验证 Dramora 前端“剧本创作 / 灵感生成”入口在登录后可选择 DeepSeek，并通过后端真实 LLM 链路生成、展示和导出 `ShortDramaScriptOutput`。

### 前端入口

- 页面：剧本创作
- 入口：灵感生成

### 模型配置

- provider：`deepseek`
- model：`deepseek-chat`
- generation_mode：`llm`

### system/status

浏览器验收时系统状态显示：

- `app_name = Dramora`
- `script_generation_mode = llm`
- `llm_enabled = true`

### 验收结果

通过。

### 验收内容

- 登录后可选择 DeepSeek；
- 登录后可从灵感生成入口发起真实 LLM 生成；
- 结果区可展示后端真实返回的 `ShortDramaScriptOutput`；
- JSON 导出可用；
- TXT 导出可用；
- Word 导出仍为后续接入状态。

### 安全说明

- 未提交 `.env`；
- 未打印 API Key；
- 未使用真实客户剧本；
- 验收样本为虚构内容。

### 后续限制

- 当前仅 idea 入口完成真实 LLM 浏览器验收；
- `film_script` / `novel` 的 LLM path 尚未接入；
- Word 导出仍需后续接入完整文档导出闭环。

## Dramora Script Generation DeepSeek Smoke Test - 2026-05-04

### 测试目标

本次测试用于小范围验收 Dramora 默认 DeepSeek 配置是否能用于三入口剧本生成链路，测试样本仅使用虚构内容，不记录 API Key，不使用真实客户剧本。

### 使用入口

- Endpoint：`POST /api/scripts/generate-from-source`
- `source_mode`：`idea`
- provider：`deepseek`
- model：`deepseek-chat`
- purpose：`script_generation`
- 测试样本：虚构短剧《测试短剧：归来之夜》

### 是否真实 llm 模式

未进入真实 LLM 调用。

第 220 步代码检查结果显示，`/api/scripts/generate-from-source` 仍直接调用 `generate_short_drama_script_mock(input_data)`，尚未根据 `SCRIPT_GENERATION_MODE=llm` 切换到真实 LLM 生成路径。因此当时未启动真实 DeepSeek 请求，避免在链路未就绪时进行无效调用或误判。

### 结果

未通过真实 DeepSeek smoke test。

阻塞点：

- `generate-from-source` endpoint 当前仍是 mock-only；
- 三入口 `ShortDramaGenerationInput` 和 `AIRequestOptions` 已具备请求结构；
- mock 输出 metadata 已可记录 provider / model / purpose；
- 但三入口服务尚未接入真实 LLM path、Prompt、JSON 解析与 `ShortDramaScriptOutput` 校验闭环。

### 返回结构摘要

本次未发起真实 curl 请求，因此无真实 DeepSeek 返回结构。

已通过安全测试：

- `.env` 存在于本地但未被 Git 跟踪；
- 配置测试与 endpoint mock 测试通过；
- 未读取 `.env` 内容；
- 未输出 API Key。

### 注意事项

- 下一步应先实现 `/api/scripts/generate-from-source` 的 `llm` path，再执行真实 DeepSeek 小样本；
- 真实 LLM path 应继续复用 `AIRequestOptions`；
- 如果用户在前端选择“后端默认”，后端应使用 `DEFAULT_LLM_PROVIDER` / `DEFAULT_SCRIPT_MODEL`；
- 不要在业务代码中硬编码 DeepSeek；
- 不记录 API Key；
- 不记录真实客户内容。

## 测试目标

本次测试用于验证 ManJuFlow 已经具备从 mock 模式切换到真实 LLM 模式的基础能力。

测试重点不是验证最终剧本质量，而是确认以下链路可以跑通：

- 通过配置切换到 `llm` 模式
- 后端读取 Prompt 文件
- 后端通过 OpenAI-compatible `LLMClient` 调用真实模型
- 模型返回内容可以解析为 JSON
- 解析结果可以通过 `ScriptOutput` 结构校验
- `/api/scripts/generate` 接口仍然作为统一入口返回结构化剧本

## 测试环境

- 本地 Mac 开发环境
- FastAPI 后端
- OpenAI-compatible `LLMClient`
- DeepSeek API
- 接口：`POST /api/scripts/generate`

## 测试输入示例

```text
一个被裁员的中年男人，意外发现公司老板用AI伪造财报
```

## 测试结果

真实 LLM 已成功返回符合 `ScriptOutput` 结构的 JSON。

返回内容包含以下核心字段和子结构：

- `project_title`
- `logline`
- `world_setting`
- `characters`
- `episodes`
- `scenes`
- `dialogues`

本次测试说明：当前后端已经可以从 mock 生成切换到真实 LLM 生成，并完成基础 JSON 解析和 Schema 校验。

## 观察到的问题

- 偶发中文异常空格
- 剧本质量还需要 Prompt 继续优化
- 多集生成稳定性尚未测试
- JSON 解析失败时还需要更完善的错误处理
- 当前尚未保存历史记录

## 中文异常空格问题与修复记录

### 问题现象

真实 LLM 输出中出现过类似异常中文空格：

- `科 技公司`
- `公 司会议室`
- `反 转`
- `二线城 市`
- `还有什 么好怕的？`

### 原因判断

Prompt 约束可以减少这类问题，但无法完全保证模型输出格式稳定。真实模型在生成长文本、中文词组、混合中英文表达时，仍可能产生异常断词或中文标点前后的多余空格。

因此仅依赖 Prompt 不够，需要在代码层增加后处理清洗能力。

### 修复方式

- 新增 `apps/api/app/services/text_cleaner.py`
- 提供 `clean_chinese_spacing`
- 支持递归处理 `dict`、`list`、`str`
- 在真实 LLM 分支中，先完成 JSON 解析，再执行中文空格清洗，最后进行 Pydantic 校验
- 清洗发生在 `ScriptOutput.model_validate(...)` 之前，避免异常空格进入最终结构化结果

### 本地测试样例

以下样例均已通过：

- `二线城 市 => 二线城市`
- `U盘 准备离开 => U盘准备离开`
- `不对 ，这些数字 => 不对，这些数字`
- `大 楼玻璃幕墙 => 大楼玻璃幕墙`
- `还有什 么好怕的？ => 还有什么好怕的？`
- `科 技公司 => 科技公司`
- `公 司会议室 => 公司会议室`
- `反 转 => 反转`

### 当前结论

- Prompt + 后处理清洗组合更稳
- 后续真实 LLM 输出仍需继续观察
- 如果未来有更多异常格式，再扩展清洗规则

## 当前结论

- 真实 LLM 链路已跑通
- 当前默认仍建议保持 `mock` 模式，保证前端演示稳定
- 后续再逐步优化 Prompt、JSON 稳定性和真实生成质量

## Storyboard LLM 测试记录

- 测试日期：2026-04-29
- 测试接口：`POST /api/storyboards/generate`
- 测试模式：`STORYBOARD_GENERATION_MODE=llm`
- 测试结果：HTTP 200 OK
- 测试输入摘要：雨夜医院门口，林晚与顾沉重逢
- 返回结构：`StoryboardOutput`
- 返回内容包含：`scene_id`、`shot_id`、`visual_description`、`ai_image_prompt_hint`
- 生成规模：模型生成 1 个 scene、7 个 shots
- 安全记录：未记录真实 API Key

本次测试说明：第二阶段 Storyboard 真实 LLM 调用链路已跑通，模型返回可通过 `StoryboardOutput` 结构承载，并保留后续“分镜 → AI 绘图 Prompt”所需的稳定字段。

## ImagePrompt DeepSeek LLM 小样本测试记录

- 测试阶段：第三阶段，分镜转 AI 绘图 Prompt
- 测试接口：`POST /api/prompts/generate`
- 测试模式：`IMAGE_PROMPT_GENERATION_MODE=llm`
- 测试目标：验证 `/api/prompts/generate` 在 `IMAGE_PROMPT_GENERATION_MODE=llm` 下可通过 DeepSeek 真实生成 `ImagePromptOutput`

模型配置：

- `LLM_BASE_URL=https://api.deepseek.com`
- `LLM_MODEL=deepseek-chat`
- `LLM_API_KEY` 已配置，但不记录真实 key
- `IMAGE_PROMPT_GENERATION_MODE=llm`

测试输入摘要：

- 项目标题：测试短剧：雨夜重逢
- 场景：医院门口雨夜重逢
- 镜头：林晚撑黑伞站在医院门口；顾沉从黑色轿车下来，两人在车灯和雨幕中对视

返回结果摘要：

- 返回合法 `ImagePromptOutput`
- 包含 2 条 `ImagePromptItem`
- `prompt_id` 包含 `P001` / `P002`
- `shot_id` 包含 `S001_SH001` / `S001_SH002`
- `positive_prompt` 为英文绘图 Prompt
- `negative_prompt` 包含 `low quality`、`blurry`、`bad anatomy`、`watermark`、`text`、`logo` 等负面词

结论：

- DeepSeek `llm` 模式小样本通过
- `parse_image_prompt_llm_response` 能成功解析真实模型输出
- `ImagePromptOutput` 数据协议可支撑真实 LLM 输出

注意事项：

- `python -m json.tool` 会将中文显示为 Unicode 转义，这是正常现象
- 测试后应切回 `IMAGE_PROMPT_GENERATION_MODE=mock`，避免日常开发消耗 token
- 后续仍需更多题材、更多镜头数量、多角色一致性测试

## ImagePrompt Mimo LLM 小样本测试记录

- 测试阶段：第三阶段，分镜转 AI 绘图 Prompt
- 测试接口：`POST /api/prompts/generate`
- 测试 provider：`mimo`
- 测试模型：`mimo-v2.5-pro`
- 测试模式：`IMAGE_PROMPT_GENERATION_MODE=llm`
- API Key 类型：`sk-` 开头的开放 API Key

Key 类型说明：

- 此前使用 `tp-` 开头 Token Plan Key 直连 `/v1/chat/completions` 返回 `401 Invalid API Key`
- 当前判断 `tp-` Key 更适合 Token Plan / 编程工具接入，不适合作为 ManJuFlow 后端直连 API Key
- `sk-` 开头 API Key 可用于 ManJuFlow 后端直连 Mimo OpenAI-compatible API

最小认证探测：

- 请求 Mimo OpenAI-compatible chat completions
- 返回 status 200
- 返回 model 为 `mimo-v2.5-pro`
- 返回 content 为 `{"ok": true}`
- 说明 `sk-` Key 可用于后端直连 API

`/api/prompts/generate` 测试结果：

- 返回合法 `ImagePromptOutput`
- 包含 2 条 `ImagePromptItem`
- `prompt_id` 包含 `P001` / `P002`
- `shot_id` 包含 `S001_SH001` / `S001_SH002`
- `positive_prompt` 为英文绘图 Prompt
- `negative_prompt` 包含 `low quality`、`blurry`、`bad anatomy`、`watermark`、`text`、`logo` 等负面词

结论：

- Mimo `llm` 模式小样本通过
- ManJuFlow 可通过 `LLM_PROVIDER=mimo` 调用 Mimo 生成 `ImagePromptOutput`

注意事项：

- 测试后应切回 `IMAGE_PROMPT_GENERATION_MODE=mock`，避免日常开发消耗额度
- 日常默认可保持 `LLM_PROVIDER=deepseek` 或 mock
- 后续需要更多题材、多镜头、多角色一致性测试
- 后续可比较 DeepSeek 与 Mimo 在画面感、格式稳定性、角色一致性、中文理解、成本和速度上的差异

## ImagePrompt Kimi LLM 小样本测试记录

- 测试阶段：第三阶段，分镜转 AI 绘图 Prompt
- 测试接口：`POST /api/prompts/generate`
- 测试 provider：`kimi`
- 测试模型：`kimi-k2.5`
- 实际返回 model 曾显示 `kimi-k2.6`
- 测试模式：`IMAGE_PROMPT_GENERATION_MODE=llm`

认证与参数记录：

- `KIMI_BASE_URL=https://api.moonshot.cn`
- `KIMI_MODEL=kimi-k2.5`
- `KIMI_API_KEY` 已配置，但不记录真实 key
- Kimi 最小认证探测通过
- Kimi k2.x 对 `temperature` 有限制，`temperature=0.1` 时返回 `invalid temperature`
- `temperature=1` 时请求通过
- `LLMClient` 已为 `kimi` provider 使用 `temperature=1.0`

`/api/prompts/generate` 测试结果：

- 返回合法 `ImagePromptOutput`
- 包含 2 条 `ImagePromptItem`
- `positive_prompt` 正常
- `negative_prompt` 正常

结论：

- Kimi `llm` 模式小样本通过

## ImagePrompt MiniMax LLM 小样本测试记录

- 测试阶段：第三阶段，分镜转 AI 绘图 Prompt
- 测试接口：`POST /api/prompts/generate`
- 测试 provider：`minimax`
- 测试模型：`MiniMax-M2.7`
- 测试模式：`IMAGE_PROMPT_GENERATION_MODE=llm`

Endpoint 记录：

- `MINIMAX_MODEL=MiniMax-M2.7`
- `MINIMAX_API_KEY` 已配置，但不记录真实 key
- 使用 `https://api.minimax.io` 返回 `401 invalid api key`
- 使用 `https://api.minimaxi.com` 返回 200
- 当前用户 MiniMax Key 对应中国区 endpoint：`MINIMAX_BASE_URL=https://api.minimaxi.com`

`/api/prompts/generate` 测试结果：

- 返回合法 `ImagePromptOutput`
- 包含 2 条 `ImagePromptItem`
- `positive_prompt` 正常
- `negative_prompt` 正常

结论：

- MiniMax `llm` 模式小样本通过

## ImagePrompt S001 四模型对比记录

- 测试阶段：第三阶段，分镜转 AI 绘图 Prompt
- 测试样本：S001 都市情感雨夜重逢
- 样本路径：`tests/fixtures/image_prompt_samples/S001_urban_rain_reunion.json`
- 结果记录：`docs/MODEL_COMPARISON_RESULTS.md`
- 输出文件目录：`tests/fixtures/image_prompt_outputs/`
- 安全记录：不记录任何 API Key

测试结果摘要：

- DeepSeek 返回合法 `ImagePromptOutput`
- Mimo 返回合法 `ImagePromptOutput`
- Kimi 返回合法 `ImagePromptOutput`
- MiniMax 返回合法 `ImagePromptOutput`
- 四家 provider 均返回 2 条 `ImagePromptItem`
- 四家 provider 均包含 `positive_prompt` / `negative_prompt`
- 四家 provider 的 `negative_prompt` 均覆盖常用负面词

问题与修复：

- Kimi 曾出现 `httpx.ReadTimeout`，后端表现为 `/api/prompts/generate` 返回 500
- 直接 httpx 请求 Kimi 使用更长 timeout 可返回 200
- 已通过 provider-specific timeout 修复：`kimi` provider 使用更长默认 timeout
- Kimi / MiniMax 中文字段存在少量异常空格
- Kimi / MiniMax 中文异常空格问题已通过 ImagePrompt parser 接入 `clean_chinese_spacing` 处理
- 后续仍需要在 S002-S004 中观察清洗效果
- 本记录不保存任何 API Key

当前结论：

- S001 第一轮四模型 ImagePrompt 对比已完成
- DeepSeek / Mimo / Kimi / MiniMax 均可支撑基础 `ImagePromptOutput` 生成
- 当前不根据单个 S001 样本确定最终默认模型
- 后续继续跑 S002-S004，再综合判断质量、稳定性、成本和速度

## 下一步建议

- 优化 `idea_to_script_v1.md`
- 增加 JSON 清洗 / 修复逻辑
- 增加错误提示
- 增加历史记录
- 再扩展到“剧本 → 分镜”
