# ManJuFlow 第三阶段进展记录：分镜转 AI 绘图 Prompt

## 阶段目标

第三阶段目标是跑通从分镜到 AI 绘图 Prompt 的结构化生产闭环：

```text
StoryboardOutput / 分镜文本
→ ImagePromptInput
→ ImagePromptOutput
→ 前端展示
→ 复制 / 导出绘图 Prompt JSON
```

第三阶段的意义：

- 从“导演分镜”进入“AI 美术绘图 Prompt 生产”
- 为后续文生图 / 图生图 / ComfyUI / 视频生成准备结构化画面描述
- 保持和前两阶段一致的数据协议、Prompt 版本化、mock 优先、测试先行原则

## 当前已完成内容

后端 Schema：

- `apps/api/app/schemas/image_prompt.py`
- `ImagePromptInput`
- `ImagePromptItem`
- `ImagePromptOutput`
- `tests/api/test_image_prompt_schema.py`
- ImagePrompt Schema 测试已通过

Prompt 文件：

- `apps/api/app/prompts/storyboard_to_image_prompt_v1.md`
- 该 Prompt 负责将分镜转成结构化绘图 Prompt JSON
- 输出必须符合 `ImagePromptOutput`
- Prompt 已版本化，后续真实 LLM 接入时可继续演进

Service：

- `apps/api/app/services/image_prompt_service.py`
- `generate_image_prompt_mock`
- `generate_image_prompt`
- `generate_image_prompt_llm`
- `load_image_prompt_template`
- `parse_image_prompt_llm_response`
- `tests/api/test_image_prompt_service.py`
- `tests/api/test_image_prompt_llm_parser.py`
- 第 69 步：ImagePrompt LLM parser 已完成
- 第 70 步：ImagePrompt mock / llm 模式切换已完成
- mock service、llm parser、generation mode 测试已通过
- Kimi provider-specific timeout 已修复，`kimi` provider 使用更长 timeout，避免 ImagePrompt 调用偶发 `ReadTimeout`
- ImagePrompt mock 相关测试已显式隔离 `IMAGE_PROMPT_GENERATION_MODE=mock`，避免受本地 `.env` 中 `llm` 模式污染
- ImagePrompt parser 已接入 `clean_chinese_spacing`
- Kimi / MiniMax ImagePrompt 中文异常空格问题已完成代码层修复，后续继续在更多样本中观察

API：

- `apps/api/app/routers/prompts.py`
- `POST /api/prompts/generate`
- `tests/api/test_image_prompt_endpoint.py`
- curl 测试已通过
- `/docs` 已能看到 `POST /api/prompts/generate`
- `/api/prompts/generate` 在 `llm` 模式下已返回合法 `ImagePromptOutput`

前端：

- `apps/web/src/types/imagePrompt.ts`
- `apps/web/src/api/imagePrompts.ts`
- 前端“生成绘图 Prompt”区域
- `ImagePromptOutput` 展示
- `positive_prompt` / `negative_prompt` 展示
- 复制绘图 Prompt JSON
- 导出绘图 Prompt JSON
- 分镜结果一键带入绘图 Prompt 生成
- 前端完整链路“灵感 → 剧本 → 分镜 → 绘图 Prompt”已通过本地浏览器验收

文档：

- `docs/API_CONTRACT.md` 已补充 `/api/prompts/generate`
- `docs/LOCAL_DEV.md` 已补充绘图 Prompt 接口测试和完整前端流水线测试
- `scripts/dev_api.sh` 已新增，用于本地启动 FastAPI 后端
- `scripts/dev_api.sh` 已修复为直接使用 venv python 执行 `python -m uvicorn app.main:app --reload`
- `scripts/kill_api_port.sh` 已新增，用于清理被 uvicorn 占用的 8000 端口
- `docs/MVP_ROADMAP.md` 已更新第三阶段进展
- `docs/MODEL_COMPARISON_PLAN.md` 已完成四模型 ImagePrompt 输出质量对比方案
- `docs/MODEL_COMPARISON_SAMPLES.md` 已完成标准样本说明
- `docs/MODEL_COMPARISON_RESULTS.md` 已记录 S001 四模型对比结果
- `docs/MODEL_COMPARISON_RUNBOOK.md` 已完成对比运行手册

## 当前验证结果

当前已知稳定结果：

- `python -m pytest tests/api` 通过，59 passed
- `npm run build` 通过
- 浏览器完整链路验收通过
- DeepSeek 真实 LLM 小样本测试已通过
- Mimo / 小米大模型 ImagePrompt 小样本测试已通过
- Kimi ImagePrompt 小样本测试已通过
- MiniMax ImagePrompt 小样本测试已通过
- DeepSeek / Mimo / Kimi / MiniMax 四个 provider 的 ImagePrompt 小样本测试均已通过
- S001 都市情感雨夜重逢样本的四模型 ImagePrompt 第一轮对比已完成
- DeepSeek / Mimo / Kimi / MiniMax 四家 provider 均通过 S001 ImagePrompt 小样本
- 四家 provider 均返回合法 `ImagePromptOutput`
- 四家 provider 均返回 2 条 `ImagePromptItem`
- S001 输出文件已保存到 `tests/fixtures/image_prompt_outputs/`
- S001 对比结果已记录到 `docs/MODEL_COMPARISON_RESULTS.md`
- `LLM_PROVIDER` 已支持四家模型
- `/api/prompts/generate` 在 `llm` 模式下已返回合法 `ImagePromptOutput`
- Kimi provider-specific timeout 已修复
- ImagePrompt 测试隔离已修复
- ImagePrompt 中文异常空格清洗已接入 parser
- 本地后端启动 / 端口清理脚本已完成：
  - `scripts/dev_api.sh`
  - `scripts/kill_api_port.sh`
- `scripts/dev_api.sh` 已修复为直接使用 venv python 启动 uvicorn
- 后端 health 已验证正常：`GET /health` 返回 `{"status":"ok","stage":"mvp-idea-to-script"}`
- 后端日志出现：
  - `POST /api/scripts/generate 200 OK`
  - `POST /api/storyboards/generate 200 OK`
  - `POST /api/prompts/generate 200 OK`
- git push 已成功，`origin/main` 已同步

## 当前边界

当前还没有做：

- S002-S004 四模型 ImagePrompt 对比尚未完成
- ImagePrompt 中文异常空格清洗已接入，后续继续观察更多样本
- 四家文本 LLM provider 已完成 ImagePrompt S001 小样本验收，但尚未做多题材、多镜头、批量质量对比
- 尚未实现前端模型选择器
- 尚未实现请求级 provider/model 动态选择
- 尚未完成第三阶段最终总结
- 还没有接入 ComfyUI
- 还没有文生图 / 图生图
- 还没有文生视频 / 图生视频
- 还没有资产管理
- 还没有任务队列
- 还没有做前端 UI 重构和美化

## 后续计划

建议按以下优先级继续推进：

1. 继续保持 mock 版稳定基线；
2. 继续完成 S002-S004 四模型 ImagePrompt 对比；
3. 汇总 DeepSeek / Mimo / Kimi / MiniMax 输出质量对比；
4. 设计请求级 provider/model 选择；
5. 设计前端模型选择器；
6. 完成第三阶段最终总结；
7. 后续再进入第四阶段：文生图 / 远端 GPU / ComfyUI；
9. 在主要功能稳定后，安排前端 UI 信息架构整理和美化。

## 质量原则

- 本项目宁愿慢一点，也要保持模块边界清晰
- 每个阶段必须有 Schema、Prompt、Service、Endpoint、Frontend、Tests、Docs
- 不为了赶进度跳过测试和文档
- 后续新增功能必须尽量减少返工
- Prompt 必须版本化
- mock 先跑通，再接真实 LLM
- 每完成一个小闭环就 commit
