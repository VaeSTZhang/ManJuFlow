# ManJuFlow｜漫剧流

ManJuFlow｜漫剧流 是一个公司内部 AI 影视化创作流水线 MVP。

当前第一阶段聚焦文本链路：从灵感输入到结构化短剧剧本输出，并通过前端页面完成演示、复制和导出。

## 第一阶段已完成能力

- 灵感输入
- 结构化短剧剧本输出
- 前端页面展示
- 复制 JSON
- 导出 JSON
- mock 模式
- 真实 LLM 模式基础接入
- DeepSeek API 本地测试通过
- 中文异常空格清洗
- 系统状态展示

## 目录结构

- `apps/api`：FastAPI 后端
- `apps/web`：React + Vite 前端
- `docs`：项目文档
- `apps/api/app/prompts`：Prompt 文件
- `apps/api/app/services`：服务层

## 本地运行

首次本地配置：

```bash
cp .env.example .env
```

真实配置文件统一放在项目根目录 `.env`。不再需要 `apps/api/.env`。

后端：

```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端：

```bash
cd apps/web
npm install
npm run dev
```

## 访问地址

- 后端健康检查：`http://127.0.0.1:8000/health`
- 后端接口文档：`http://127.0.0.1:8000/docs`
- 前端页面：`http://localhost:5173/`

## 模式说明

默认推荐使用 mock 模式，适合本地演示和前端联调：

```env
SCRIPT_GENERATION_MODE=mock
```

真实 LLM 测试模式：

```env
SCRIPT_GENERATION_MODE=llm
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_API_KEY=请放在本地 .env，不要提交
```

## 安全提醒

- 不要提交 `.env`
- `.env` 统一放在项目根目录
- 不要创建或依赖 `apps/api/.env`
- 不要把 API Key 写进代码
- 不要把 API Key 发给任何 AI
- `.env.example` 只保留字段名

## 当前暂不做

- 文生图
- 文生视频
- ComfyUI
- n8n
- Redis
- MinIO
- 自动剪辑
- 完整服务器部署

## 下一阶段方向

- 优化真实 LLM 剧本质量
- 增加历史记录
- 增加导出格式
- 扩展到“剧本 → 分镜”
- 扩展到“分镜 → 绘图 Prompt”
