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

## 后端启动方式

```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 后端访问地址

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

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

## 前端流水线测试：灵感 → 剧本 → 分镜

- 启动后端，确保服务运行在 `http://127.0.0.1:8000`
- 启动前端，确保页面运行在 `http://localhost:5173`
- 打开 `http://localhost:5173`
- 在灵感输入区域填写或使用默认内容
- 点击“生成结构化剧本”
- 在结构化剧本结果区域点击“带入分镜生成”
- 检查“生成分镜”区域的项目标题和剧本文本是否已自动填入
- 点击“生成分镜”
- 检查分镜结果是否正常展示 scenes / shots
- 测试结构化剧本的“复制 JSON”和“导出 JSON”
- 测试分镜结果的“复制分镜 JSON”和“导出分镜 JSON”

## 常见问题

- `npm: command not found`：需要安装 Node.js
- `OPTIONS 405`：需要确认后端 CORS 已配置
- GitHub push 失败：可能是网络波动，可稍后重试
