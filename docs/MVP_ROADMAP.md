# ManJuFlow｜漫剧流 MVP Roadmap

## 第一阶段目标

- 灵感输入
- 结构化短剧剧本输出
- 前端页面展示
- 可复制 / 可导出结果

## 当前已完成

- 项目初始化
- FastAPI `/health`
- 核心 Schema
- `/api/scripts/generate` mock
- GitHub 初次推送
- Storyboard Schema 已完成
- `script_to_storyboard_v1.md` 已完成
- Storyboard mock service 已完成
- `/api/storyboards/generate` 已完成
- 前端生成分镜 UI 已完成
- 前端“剧本 → 分镜”衔接已完成
- Storyboard service 字段覆盖测试已完成
- 第二阶段本地稳定验收已通过

## 下一步计划

- 继续打磨剧本转分镜的 mock 输出质量
- 评估后续真实 LLM 接入方式
- 继续保持前后端接口契约稳定

## 当前暂不做

- 文生图
- 文生视频
- ComfyUI
- n8n
- Redis
- MinIO
- 复杂多 Agent
- Docker 部署

## 项目推进原则

- 每次只做一个小闭环
- 每个阶段完成后 commit
- 后端、前端、Prompt、模型接入分阶段推进
