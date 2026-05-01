# ManJuFlow 四模型 ImagePrompt 对比运行手册

## 1. 目的

- 本文档用于指导如何安全执行 DeepSeek / Mimo / Kimi / MiniMax 的标准样本对比；
- 标准输入来自 `tests/fixtures/image_prompt_samples/`；
- 结果记录到 `docs/MODEL_COMPARISON_RESULTS.md`；
- 本文档强调先小样本、再完整对比，避免误耗 token / credits。

## 2. 当前 provider 状态

- `deepseek`：已通过 ImagePrompt 小样本；
- `mimo`：已通过 ImagePrompt 小样本；
- `kimi`：已通过 ImagePrompt 小样本，`temperature=1.0` 已适配；
- `minimax`：已通过 ImagePrompt 小样本，中国区 endpoint 为 `https://api.minimaxi.com`。

## 3. 安全前置检查

1. 确认 `git status` clean；
2. 确认 `.env` 不会被提交；
3. 确认默认状态为 `IMAGE_PROMPT_GENERATION_MODE=mock`；
4. 确认四家 provider 的 API Key 已配置，但不要打印真实 key；
5. 每次真实测试后必须切回 mock；
6. 修改 `.env` 后必须重启后端；
7. 前端不需要重启，除非本轮测试涉及前端代码。

## 4. 推荐执行策略

- 第一轮只跑 S001 x 4 providers；
- 确认流程稳定后，再跑 S001-S004 x 4 providers；
- 不建议一开始直接批量跑 16 次；
- 每轮测试后把输出复制保存；
- 若某 provider 报错，先记录异常，不要立刻大改代码。

## 5. 输出文件命名建议

建议后续创建目录：

```text
tests/fixtures/image_prompt_outputs/
```

输出命名：

```text
S001_deepseek_output.json
S001_mimo_output.json
S001_kimi_output.json
S001_minimax_output.json
```

完整对比时：

```text
S002_deepseek_output.json
...
S004_minimax_output.json
```

说明：

- 输出文件暂时可作为人工评估材料；
- 不保存 API Key；
- 若输出包含明显敏感信息，应脱敏后再提交；
- 是否提交真实模型输出，需要后续确认。

## 6. 手动测试流程

1. 设置 `LLM_PROVIDER`；
2. 设置 `IMAGE_PROMPT_GENERATION_MODE=llm`；
3. 重启后端；
4. 使用 fixture JSON 调用 `/api/prompts/generate`；
5. 将返回结果保存为输出 JSON；
6. 检查是否为合法 `ImagePromptOutput`；
7. 记录 latency / error / notes；
8. 切回 `IMAGE_PROMPT_GENERATION_MODE=mock`；
9. 重启后端恢复安全状态。

## 7. 推荐 curl 模板

使用 S001 fixture：

```bash
curl -s -X POST http://127.0.0.1:8000/api/prompts/generate \
  -H "Content-Type: application/json" \
  --data-binary @tests/fixtures/image_prompt_samples/S001_urban_rain_reunion.json \
  | python -m json.tool
```

说明：

- provider 由 `.env` 中 `LLM_PROVIDER` 决定；
- 运行前必须重启后端；
- 输出可以重定向到临时文件；
- 不要直接覆盖已有结果。

## 8. 异常处理

- 401 / 403：API Key 或 endpoint 问题；
- 400：模型参数、模型名或请求体问题；
- 500：后端 parser / schema 校验 / LLM 输出不稳定；
- JSON tool 报 `Expecting value`：后端可能返回非 JSON，查看后端日志；
- 超时：记录 provider、sample_id、请求耗时，暂不重试太多次。

## 9. 暂不自动化

- 暂不做自动批量调用脚本；
- 暂不做自动评分；
- 暂不做前端模型选择器；
- 暂不把结果写入数据库；
- 先通过手动小样本验证流程稳定性。

## 10. 下一步

1. 先执行 S001 x 4 providers；
2. 将输出保存为本地临时文件或后续 fixture；
3. 人工打分并填写 `docs/MODEL_COMPARISON_RESULTS.md`；
4. 再决定是否跑完整 16 组；
5. 若流程稳定，再考虑写一个本地脚本辅助运行。
