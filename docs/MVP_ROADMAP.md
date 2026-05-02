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
- Kimi ImagePrompt 小样本测试已通过
- MiniMax ImagePrompt 小样本测试已通过
- 四家 provider：DeepSeek / Mimo / Kimi / MiniMax 均已通过 ImagePrompt 小样本验收
- S001 四模型 ImagePrompt 对比完成
- ImagePrompt 输出文件已保存到 `tests/fixtures/image_prompt_outputs/`
- provider-specific timeout 已完成，Kimi provider 使用更长 timeout
- ImagePrompt 测试隔离已修复，后端 `tests/api` 当前为 58 passed
- ImagePrompt 中文空格清洗已完成
- 后端 `tests/api` 当前为 59 passed
- 本地后端启动脚本已完成：`scripts/dev_api.sh`
- 后端启动脚本兼容性修复已完成：`scripts/dev_api.sh` 直接使用 venv python 启动 uvicorn
- 本地后端端口清理脚本已完成：`scripts/kill_api_port.sh`
- 请求级 provider/model 选择完成
- 前端 ImagePrompt 模型选择器完成
- 前端模型选择器浏览器验收通过
- README 公开项目展示优化完成
- 第三阶段总结文档已创建：`docs/PHASE_3_SUMMARY.md`
- 第四阶段文生图 / 远端 GPU / ComfyUI 方案文档已完成：`docs/PHASE_4_IMAGE_GENERATION_PLAN.md`
- ImageGeneration Schema 已完成
- mock image generation service 已完成
- `POST /api/images/generate` 已完成
- 前端 ImageGeneration 类型和 API 封装已完成
- 前端 Image Generation mock UI 已完成
- 浏览器 mock 联调已通过
- 手动 `prompt_items` JSON → `/api/images/generate` → mock 图片结果已通过
- `ImagePromptResult` → `/api/images/generate` → mock 图片结果已通过
- 当前仍未接真实 ComfyUI / GPU

## 下一步计划

- S002-S004 模型对比
- 合作技术资产与权属边界说明文档
- 第四阶段接口与本地开发文档更新
- 第四阶段进度文档补全
- 设计 ComfyUI adapter interface
- 新增私有部署 runbook 草案
- S002-S004 可作为后续模型质量补充对比

## 当前暂不做

- 真实文生图
- 文生视频
- 真实 ComfyUI 接入
- 真实 GPU 服务器接入
- n8n
- Redis
- MinIO
- 复杂多 Agent
- Docker 部署

## 项目推进原则

- 每次只做一个小闭环
- 每个阶段完成后 commit
- 后端、前端、Prompt、模型接入分阶段推进
