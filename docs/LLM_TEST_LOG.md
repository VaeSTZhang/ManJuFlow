# ManJuFlow 真实 LLM 调用测试记录

## 测试目标

本次测试用于验证 ManJuFlow 已经具备从 mock 模式切换到真实 LLM 模式的基础能力。

测试重点不是验证最终剧本质量，而是确认以下链路可以跑通：

- 通过配置切换到 `llm` 模式
- 后端读取 Prompt 文件
- 后端通过 OpenAI-compatible `LLMClient` 调用真实模型
- 模型返回内容可以解析为 JSON
- 解析结果可以通过 `ScriptOutput` 结构校验
- `/api/scripts/generate` 接口仍然作为统一入口返回结构化剧本

## 测试环境

- 本地 Mac 开发环境
- FastAPI 后端
- OpenAI-compatible `LLMClient`
- DeepSeek API
- 接口：`POST /api/scripts/generate`

## 测试输入示例

```text
一个被裁员的中年男人，意外发现公司老板用AI伪造财报
```

## 测试结果

真实 LLM 已成功返回符合 `ScriptOutput` 结构的 JSON。

返回内容包含以下核心字段和子结构：

- `project_title`
- `logline`
- `world_setting`
- `characters`
- `episodes`
- `scenes`
- `dialogues`

本次测试说明：当前后端已经可以从 mock 生成切换到真实 LLM 生成，并完成基础 JSON 解析和 Schema 校验。

## 观察到的问题

- 偶发中文异常空格
- 剧本质量还需要 Prompt 继续优化
- 多集生成稳定性尚未测试
- JSON 解析失败时还需要更完善的错误处理
- 当前尚未保存历史记录

## 当前结论

- 真实 LLM 链路已跑通
- 当前默认仍建议保持 `mock` 模式，保证前端演示稳定
- 后续再逐步优化 Prompt、JSON 稳定性和真实生成质量

## 下一步建议

- 优化 `idea_to_script_v1.md`
- 增加 JSON 清洗 / 修复逻辑
- 增加错误提示
- 增加历史记录
- 再扩展到“剧本 → 分镜”
