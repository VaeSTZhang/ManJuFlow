# ManJuFlow｜漫剧流本地开发运行说明

## 前置条件

- Python 3.12+
- Node.js / npm
- Git

## 本地配置文件

真实配置文件统一放在项目根目录 `.env`。

可以从模板创建本地配置：

```bash
cp .env.example .env
```

注意：

- 不要提交 `.env`
- 不再需要 `apps/api/.env`
- 后端从 `apps/api` 启动时，也会读取项目根目录 `.env`

## 生成模式配置

默认使用 mock 模式，适合本地演示和测试：

```env
SCRIPT_GENERATION_MODE=mock
STORYBOARD_GENERATION_MODE=mock
IMAGE_PROMPT_GENERATION_MODE=mock
```

`STORYBOARD_GENERATION_MODE` 支持 `mock` / `llm`。当前 Storyboard 真实 LLM 尚未正式接入，即使配置为 `llm`，服务层也会暂时 fallback 到 mock；后续接真实 LLM 时再补充 JSON 解析、Schema 校验与修复逻辑。

`IMAGE_PROMPT_GENERATION_MODE` 支持：

- `mock`：默认，本地 mock 输出，不调用真实 LLM，适合前端联调。
- `llm`：调用 `LLMClient`，并解析为 `ImagePromptOutput`。

修改 `.env` 后需要重启后端 `uvicorn`。`llm` 模式需要确保已有 LLM API 配置可用，建议先用小样本测试，不要直接大批量调用。

## 后端启动方式

```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 后端重启与端口占用处理

以下情况需要重启后端：

- 修改 `.env`
- 修改 `LLM_PROVIDER`
- 修改 `*_GENERATION_MODE`
- 修改后端 Python 代码
- 修改依赖
- 遇到 `Address already in use`
- 后端状态疑似没读到最新配置

推荐使用脚本启动后端：

```bash
bash scripts/dev_api.sh
```

`scripts/dev_api.sh` 当前会直接定位虚拟环境中的 Python，并执行 `python -m uvicorn app.main:app --reload`。它不再依赖 `source activate`，避免严格 shell 选项下激活脚本提前退出。

如果遇到端口占用：

```bash
bash scripts/kill_api_port.sh
bash scripts/dev_api.sh
```

也可以使用原始手动命令：

```bash
cd apps/api
source .venv/bin/activate 2>/dev/null || source ../../.venv/bin/activate
uvicorn app.main:app --reload
```

说明：

- 前端代码未变化时，前端不需要重启。
- 只切换后端 provider / `.env` 时，通常只需要重启后端。
- 当前模型对比流程中，每次切换 `LLM_PROVIDER` 后都需要重启后端。
- 测试结束后切回 `IMAGE_PROMPT_GENERATION_MODE=mock` 后，也需要重启后端恢复安全状态。
- 前端 ImagePrompt 模型选择器可用于本地选择 provider。
- 切换前端模型选择器本身不需要重启后端。
- mock 模式下前端模型选择器不会调用真实 LLM。
- llm 模式下需要后端 `.env` 配置对应 provider 的 API Key。

## 后端访问地址

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## 运行后端测试

安装依赖：

```bash
pip install -r apps/api/requirements.txt
```

当前推荐一起运行四类 Storyboard 测试：

```bash
python -m pytest tests/api/test_storyboard_service.py tests/api/test_storyboard_endpoint.py tests/api/test_storyboard_schema.py tests/api/test_storyboard_llm_parser.py
```

`test_storyboard_service.py` 用于确认 Storyboard mock service 返回 `scene_id`、`shot_id`、`visual_description`、`ai_image_prompt_hint` 等后续流水线需要的关键字段。

当前 Storyboard service 测试也覆盖 generation mode 行为：

- `STORYBOARD_GENERATION_MODE=mock` 正常生成
- `STORYBOARD_GENERATION_MODE=llm` 当前 fallback mock
- 非法 mode 会抛出 `ValueError`

`test_storyboard_endpoint.py` 用于验证 `POST /api/storyboards/generate` 返回稳定 `StoryboardOutput`。

`test_storyboard_schema.py` 用于验证 Storyboard Schema 会拒绝空标题、空剧本、空 `scenes`、空 `shots`、空 `visual_description` 和非正数 `duration_seconds`。

`test_storyboard_llm_parser.py` 用于验证 LLM 原始文本到 `StoryboardOutput` 的解析与校验，覆盖纯 JSON、Markdown code fence、空文本、非法 JSON、Schema 不匹配等情况。

## 本地测试分镜接口

启动后端后，可以直接测试剧本转分镜接口：

```bash
curl -X POST "http://127.0.0.1:8000/api/storyboards/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_title": "测试短剧：雨夜重逢",
    "script_text": "第1集 第1场｜医院门口｜雨夜。暴雨中，林晚撑着黑伞站在医院门口，顾沉从车里下来，两人隔雨对视。顾沉：你终于肯回来了？林晚：我回来，不是为了见你。"
  }'
```

后端接口文档可以在 `http://127.0.0.1:8000/docs` 查看。

## 本地测试绘图 Prompt 接口

启动后端：

```bash
cd apps/api
source .venv/bin/activate 2>/dev/null || source ../../.venv/bin/activate
uvicorn app.main:app --reload
```

测试以下地址：

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/api/system/status`
- `POST http://127.0.0.1:8000/api/prompts/generate`

curl 示例：

```bash
curl -X POST "http://127.0.0.1:8000/api/prompts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_title": "测试短剧：雨夜重逢",
    "storyboard_summary": "医院门口雨夜重逢，男女主在冷色车灯和雨幕中对峙。",
    "storyboard_text": "第1场｜医院门口｜雨夜。镜头1：林晚撑着黑伞站在医院门口台阶边，雨水打湿地面。镜头2：顾沉从黑色轿车里下来，两人在车灯和雨幕中对视。",
    "target_model": "general",
    "aspect_ratio": "9:16",
    "style_preset": "cinematic realistic",
    "language": "en",
    "extra_requirements": "保持雨夜、冷色光影、电影感写实风格。"
  }'
```

打开接口文档：

- `http://127.0.0.1:8000/docs`

确认可以看到：

- `POST /api/prompts/generate`

## 前端启动方式

```bash
cd apps/web
npm install
npm run dev
```

## 前端访问地址

- `http://localhost:5173/`

## 使用流程

- 先启动后端
- 再启动前端
- 在网页输入灵感
- 点击“生成结构化剧本”
- 查看结果
- 使用“复制 JSON”

## 前端分镜功能测试

- 确认后端运行在 `http://127.0.0.1:8000`
- 确认前端运行在 `http://localhost:5173`
- 打开 `http://localhost:5173`
- 找到“生成分镜”区域
- 输入项目标题和剧本文本
- 点击“生成分镜”
- 查看分镜结果
- 测试“复制分镜 JSON”和“导出分镜 JSON”

## 前端完整流水线测试：灵感 → 剧本 → 分镜 → 绘图 Prompt

启动后端：

```bash
cd apps/api
source .venv/bin/activate 2>/dev/null || source ../../.venv/bin/activate
uvicorn app.main:app --reload
```

启动前端：

```bash
cd apps/web
npm run dev
```

访问：

- `http://localhost:5173/`

测试步骤：

1. 在灵感输入区填写或使用默认内容。
2. 点击“生成结构化剧本”。
3. 检查剧本结果正常展示。
4. 点击“带入分镜生成”。
5. 检查分镜生成区已自动填入项目标题和剧本文本。
6. 点击“生成分镜”。
7. 检查分镜结果正常展示 scenes / shots。
8. 点击“带入绘图 Prompt 生成”或“用此分镜生成绘图 Prompt”。
9. 检查绘图 Prompt 输入区已自动填入项目标题、分镜摘要、分镜文本 / JSON。
10. 点击“生成绘图 Prompt”。
11. 检查绘图 Prompt 结果正常展示 items、positive_prompt、negative_prompt。
12. 测试复制绘图 Prompt JSON。
13. 测试导出绘图 Prompt JSON。

后端日志应看到：

- `POST /api/scripts/generate 200 OK`
- `POST /api/storyboards/generate 200 OK`
- `POST /api/prompts/generate 200 OK`

补充说明：

- 当前第三阶段仍是 mock 模式。
- 不会调用真实图片生成模型。
- 不会调用 ComfyUI。
- 当前 `ImagePromptOutput` 用于验证数据协议和前端闭环。
- 后续再接入真实 LLM 和 Mimo / 小米大模型。

## 常见问题

- `npm: command not found`：需要安装 Node.js
- `OPTIONS 405`：需要确认后端 CORS 已配置
- GitHub push 失败：可能是网络波动，可稍后重试
