# ManJuFlow 第二阶段总结：剧本转分镜

## 一、阶段目标

- 结构化剧本 / 剧本文本 → `StoryboardOutput`
- 前端展示
- 复制 / 导出分镜 JSON
- 支持 mock 与真实 LLM 两种模式

## 二、已完成能力

- StoryboardInput / StoryboardOutput Schema
- `scene_id` / `shot_id` / `visual_description` 稳定字段
- `script_to_storyboard_v1.md` Prompt
- `storyboard_service` mock 模式
- `STORYBOARD_GENERATION_MODE=mock / llm`
- `generate_storyboard_llm`
- `parse_storyboard_llm_response`
- `POST /api/storyboards/generate`
- 前端分镜生成 UI
- 剧本结果一键带入分镜输入
- 分镜展示
- 复制分镜 JSON
- 导出分镜 JSON
- Storyboard service 测试
- endpoint 测试
- schema 约束测试
- llm parser 测试
- 真实 LLM 本地调用测试
- 前端 llm 模式完整验收

## 三、核心文件清单

后端：

- `apps/api/app/schemas/storyboard.py`
- `apps/api/app/prompts/script_to_storyboard_v1.md`
- `apps/api/app/services/storyboard_service.py`
- `apps/api/app/routers/storyboards.py`
- `apps/api/app/main.py`

前端：

- `apps/web/src/types/storyboard.ts`
- `apps/web/src/api/storyboards.ts`
- `apps/web/src/App.tsx`
- `apps/web/src/App.css`

测试：

- `tests/api/test_storyboard_service.py`
- `tests/api/test_storyboard_endpoint.py`
- `tests/api/test_storyboard_schema.py`
- `tests/api/test_storyboard_llm_parser.py`

文档：

- `docs/API_CONTRACT.md`
- `docs/LOCAL_DEV.md`
- `docs/MVP_ROADMAP.md`
- `docs/PHASE_2_PROGRESS.md`
- `docs/LLM_TEST_LOG.md`
- `docs/PHASE_2_SUMMARY.md`

## 四、最终验收结果

- pytest 16 passed
- `npm run build` 通过
- `GET /health` 200 OK
- `POST /api/storyboards/generate` 200 OK
- `STORYBOARD_GENERATION_MODE=llm` 真实调用通过
- 前端“灵感 → 剧本 → 分镜”完整链路通过
- 分镜 JSON 可复制、可导出
- `git status` clean
- `origin/main` 已同步

## 五、当前仍未做

- 未做数据库保存
- 未做历史记录
- 未做复杂 JSON 自动修复
- 未做分镜质量评分
- 未做 AI 绘图 Prompt 生成
- 未接入文生图 / 图生图
- 未接入文生视频
- 未接入 ComfyUI / Redis / MinIO / n8n

## 六、阶段结论

- 第二阶段已经达到和第一阶段同等质量标准
- 不仅有 mock、前端和文档，也已完成真实 LLM 本地调用测试
- `StoryboardOutput` 已具备作为第三阶段“分镜 → AI 绘图 Prompt”的稳定输入

## 七、下一阶段建议

- 第三阶段建议开始“分镜 → AI 绘图 Prompt”
- 第一步应先定义 ImagePrompt Schema
- 再写 `storyboard_to_image_prompt_v1.md`
- 再做 `prompt_service` mock
- 再做 `/api/prompts/generate`
- 再接前端展示与导出
