# ManJuFlow 第二阶段进度记录：剧本转分镜

## 一、阶段目标

第二阶段目标是完成从剧本文本或结构化剧本到分镜结果的最小闭环：

```text
剧本文本 / 结构化剧本 → StoryboardOutput → 前端展示 → 复制 / 导出分镜 JSON
```

当前阶段聚焦可用的结构化输出与前端演示，不接入真实 LLM、不做数据库保存、不做图片或视频生成。

## 二、已完成能力

- StoryboardInput / StoryboardOutput Schema
- Storyboard 中已补充 `scene_id`、`shot_id`、`visual_description`，用于后续“分镜 → AI 绘图 Prompt”的稳定衔接
- `script_to_storyboard_v1.md` Prompt
- `storyboard_service` mock service
- `POST /api/storyboards/generate`
- 前端生成分镜 UI
- 分镜结果展示
- 复制分镜 JSON
- 导出分镜 JSON
- 结构化剧本结果可一键带入分镜生成输入
- 前端已形成“灵感 → 剧本 → 分镜”的最小流水线体验
- API 文档与本地开发文档更新

## 三、核心文件清单

后端：

- `apps/api/app/schemas/storyboard.py`
- `apps/api/app/prompts/script_to_storyboard_v1.md`
- `apps/api/app/services/storyboard_service.py`
- `apps/api/app/routers/storyboards.py`
- `apps/api/app/main.py`
- `tests/api/test_storyboard_service.py`

前端：

- `apps/web/src/types/storyboard.ts`
- `apps/web/src/api/storyboards.ts`
- `apps/web/src/App.tsx`
- `apps/web/src/App.css`

文档：

- `docs/API_CONTRACT.md`
- `docs/LOCAL_DEV.md`
- `docs/MVP_ROADMAP.md`
- `docs/PHASE_2_PROGRESS.md`

## 四、本地演示步骤

1. 启动后端。
2. 启动前端。
3. 打开 `http://localhost:5173`。
4. 使用页面中默认测试剧本文本。
5. 点击“生成分镜”。
6. 检查分镜展示、复制 JSON、导出 JSON。

也可以先在灵感输入区域生成结构化剧本，再点击“带入分镜生成”，将剧本结果自动填入分镜输入区域后继续生成分镜。

后端启动命令：

```bash
cd apps/api
uvicorn app.main:app --reload
```

前端启动命令：

```bash
cd apps/web
npm run dev
```

curl 测试 `/api/storyboards/generate`：

```bash
curl -X POST "http://127.0.0.1:8000/api/storyboards/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_title": "测试短剧：雨夜重逢",
    "script_text": "第1集 第1场｜医院门口｜雨夜。暴雨中，林晚撑着黑伞站在医院门口，顾沉从车里下来，两人隔雨对视。顾沉：你终于肯回来了？林晚：我回来，不是为了见你。"
  }'
```

## 五、验收标准

- [ ] 后端 `/docs` 能看到 `POST /api/storyboards/generate`
- [ ] curl 返回 StoryboardOutput JSON
- [ ] 前端能生成分镜
- [ ] 剧本结果可一键带入分镜输入
- [ ] 带入后可继续生成分镜
- [ ] 页面能展示 scenes / shots
- [ ] 分镜 JSON 中包含 `scene_id`、`shot_id`、`visual_description`
- [ ] Storyboard service 自动测试通过：`python -m pytest tests/api/test_storyboard_service.py`
- [ ] 复制 JSON 可用
- [ ] 导出 JSON 可用
- [ ] `npm run build` 通过
- [ ] `git status` clean

## 六、当前仍是 mock 的部分

- 当前 `storyboard_service` 默认使用 `STORYBOARD_GENERATION_MODE=mock`
- `STORYBOARD_GENERATION_MODE` 已预留 `llm` 模式，但暂未正式接入真实 LLM；当前 `llm` 模式仍 fallback 到 mock
- `script_to_storyboard_v1.md` Prompt 已要求 `scene_id`、`shot_id`、`visual_description`，为后续真实 LLM 接入和绘图 Prompt 阶段做准备
- 尚未接入真实 LLM
- 尚未做模型 JSON 解析与修复
- 尚未做数据库保存
- 尚未生成绘图 Prompt
- 尚未接入图片或视频生成

## 七、下一步建议

后续建议开始第三阶段：分镜 → AI 绘图 Prompt。

建议顺序：

1. 先定义 ImagePrompt Schema。
2. 再写 `storyboard_to_image_prompt_v1.md`。
3. 再做 mock service。
4. 再做 `/api/prompts/generate`。
5. 最后接前端展示。

## 八、稳定验收状态

当前第二阶段 MVP+加固版已通过本地验收。

已验证：

- Storyboard service pytest 通过
- 前端 `npm run build` 通过
- `/api/storyboards/generate` curl 返回正常
- 前端“灵感 → 剧本 → 分镜”流水线可用
- `scene_id` / `shot_id` / `visual_description` 字段可见并可导出
- `git status` clean

当前阶段仍未接入真实 LLM，`storyboard_service` 仍是 mock service；但接口、Schema、Prompt、前端、测试和文档已经具备后续扩展基础。
