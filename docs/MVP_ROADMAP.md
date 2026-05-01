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
- Storyboard generation mode 测试覆盖已完成
- Storyboard endpoint 测试已完成
- Storyboard Schema 约束测试已完成
- Storyboard LLM 输出解析测试已完成
- Storyboard LLM 真实调用测试已完成
- 第二阶段本地稳定验收已通过
- 第二阶段最终总结已完成
- 第三阶段已开始：分镜 → AI 绘图 Prompt
- ImagePrompt Schema 已完成
- `storyboard_to_image_prompt_v1.md` 已完成
- ImagePrompt mock service 已完成
- `/api/prompts/generate` 已完成
- mock 模式 curl 测试已通过
- 前端 ImagePrompt 类型和 API 封装已完成
- 前端“生成绘图 Prompt”区域已完成
- 绘图 Prompt JSON 复制 / 导出已完成
- 分镜结果一键带入绘图 Prompt 生成已完成
- 前端完整链路“灵感 → 剧本 → 分镜 → 绘图 Prompt”已通过本地验收
- ImagePrompt LLM parser 已完成
- ImagePrompt mock / llm 模式切换已完成
- `IMAGE_PROMPT_GENERATION_MODE` 已加入配置
- 后端 `tests/api` 已扩展到 44 passed
- ImagePrompt DeepSeek 真实 LLM 小样本测试已通过
- `/api/prompts/generate` llm 模式已通过小样本验收
- `LLM_PROVIDER=deepseek / mimo` 配置支持已完成
- Mimo / 小米大模型 ImagePrompt 小样本测试已通过
- Mimo `sk-` API Key 可用于后端直连 API

## 下一步计划

- 补充第三阶段进展文档
- 后续接入真实 LLM 前，继续保持 mock 小闭环可测试
- 模型效果对比
- 更多样本测试
- 第三阶段总结
- `LLM_TEST_LOG` 更新

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
