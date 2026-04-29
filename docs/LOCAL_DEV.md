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

## 常见问题

- `npm: command not found`：需要安装 Node.js
- `OPTIONS 405`：需要确认后端 CORS 已配置
- GitHub push 失败：可能是网络波动，可稍后重试
