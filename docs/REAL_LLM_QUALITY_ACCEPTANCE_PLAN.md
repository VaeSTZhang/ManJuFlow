# Real LLM Quality Acceptance Plan｜真实模型质量验收计划

## 1. 验收目标

真实模型质量验收不是为了跑分，也不是为了证明某个模型在所有场景中最优，而是为了在老板实操和内部试用前确认 Dramora 的三入口生成 / 改编链路在真实 LLM 下可用、稳定、可解释、错误可处理。

本计划重点确认：

- 三入口能在真实模型模式下稳定返回结构化 `ShortDramaScriptOutput`；
- 输出质量足以进入内部审看、在线编辑和导出；
- 模型失败、超时、结构异常时有清晰处理路径；
- 测试样本、日志和文档不暴露 API Key、真实客户内容或合作方敏感信息。

## 2. 模型范围

当前至少覆盖以下 provider：

- DeepSeek：默认推荐模型，必须完整验收；
- Mimo：已配置 provider，建议抽检；
- Kimi：已配置 provider，建议抽检；
- MiniMax：已配置 provider，建议抽检。

前端 e2e 已覆盖 DeepSeek / Mimo / Kimi / MiniMax 的 `ai_options.provider` 和 `ai_options.model` 请求 payload，这只能证明传参正确，不代表真实模型输出质量可用。

真实 API 验收不要求每次全量跑四家模型。DeepSeek 作为默认推荐模型应完整覆盖三入口；Mimo / Kimi / MiniMax 可按成本、稳定性和内部试用需要做抽检，避免不必要的费用和外部服务波动。

## 3. 三入口验收范围

必须覆盖：

- `idea`：灵感生成短剧剧本；
- `film_script`：电影剧本改编短剧本；
- `novel`：小说 / 网文改编短剧本。

三入口均应验证：

- 请求能携带 `AIRequestOptions`；
- 后端能调用对应 source_mode 的真实 LLM path；
- 返回结果能通过 schema 校验；
- 前端能展示、编辑、复制 JSON、下载 TXT / JSON / Word。

## 4. 安全样本原则

所有真实模型验收输入必须是安全虚构内容：

- 不使用真实客户剧本；
- 不使用真实电影完整剧本；
- 不使用真实小说原文；
- 不使用合作方敏感内容；
- 不使用个人隐私、内部合同、商务资料或未公开项目资料；
- 不提交真实模型完整输出到公开仓库；
- 不在日志中记录 API Key、`.env` 内容或服务器路径。

验收记录只保留输入摘要、输出结构摘要、质量评价和问题结论。

## 5. 建议测试样本

### idea 小样本

项目标题：测试短剧：旧楼灯火

灵感内容：

一个年轻短剧编剧离开城市三年后回到即将拆迁的旧楼，发现父亲生前留下的一份未完成剧本，竟然预告了公司新项目被盗的真相。她必须在拆迁前夜找出背叛者，并完成父亲留下的最后一场戏。

要求：

- 3 集；
- 都市职场 + 家庭悬疑；
- 每集结尾有强钩子；
- 对白自然，冲突快。

### film_script 小样本

项目标题：测试短剧：被偷走的首映夜

虚构电影剧本片段：

首映礼前夜，制片人周岚发现导演署名被临时替换。会议室里，投资人要求她沉默，主演沈越却偷偷递给她一只旧录音笔。录音里传来三年前失踪编剧的声音，说真正的剧本结局藏在道具仓库的红色箱子里。

改编方向：

- 改成 3 集短剧；
- 保留“作品署名被窃取”的主冲突；
- 强化女性主角反击线；
- 每集必须有反转和情绪爆点。

### novel 小样本

项目标题：测试短剧：书店第七盏灯

虚构小说片段：

南城旧书店每晚只亮七盏灯。林乔回到书店处理母亲遗物时，发现每一本被标记的旧书都对应一个她童年遗忘的人。邻居程砚提醒她不要打开第七盏灯下的木箱，但林乔在箱子里找到了母亲写给未来自己的信。

改编方向：

- 改成 3 集女性成长短剧；
- 强化亲情、秘密和自我和解；
- 弱化支线人物；
- 每集结尾留下悬念。

## 6. 验收维度

结构维度：

- 返回 JSON 是否可解析；
- 是否符合 `ShortDramaScriptOutput`；
- 是否包含 `project_title`、`logline`、`world_setting`、`characters`、`episodes`；
- `characters` 是否至少包含主要角色；
- `episodes` 是否符合目标集数或有合理解释；
- metadata 是否包含 `generation_mode`、`provider`、`model`、`purpose`。

内容维度：

- 短剧感是否明显；
- 分集钩子是否足够；
- 对白是否自然、短促、有冲突；
- 角色动机是否清楚；
- 世界观 / 故事背景是否能支撑剧情；
- 输出是否过短、过长或结构空泛；
- 是否有明显胡编乱造或自相矛盾。

入口专项：

- `idea`：是否能把灵感扩成完整短剧结构；
- `film_script`：是否保留主冲突、核心人物关系和关键情绪；
- `novel`：是否提炼人物关系、主线矛盾和短剧化节奏。

产品闭环：

- 是否能进入在线编辑；
- 编辑后复制 JSON 是否使用编辑稿；
- 编辑后下载 TXT / JSON / Word 是否使用编辑稿；
- 前端错误提示是否产品化；
- 是否没有用户可见的开发态文案。

安全合规：

- 是否出现敏感或不合规内容；
- 是否泄露 prompt、API Key、服务器路径或内部配置；
- 是否误把测试样本当成真实案例。

## 7. 运行方式建议

运行前确认：

- 真实配置只放项目根目录 `.env`；
- `.env` 不提交；
- 不 `cat`、不打印、不过度 grep `.env`；
- `SCRIPT_GENERATION_MODE=llm`；
- 默认验收使用 `DEFAULT_LLM_PROVIDER=deepseek`；
- 默认脚本模型使用 `DEFAULT_SCRIPT_MODEL=deepseek-chat` 或当前配置的等价字段；
- `DEEPSEEK_API_KEY` 已在本地安全配置。

建议使用本地后端和小样本请求：

```bash
curl -s -X POST http://127.0.0.1:8000/api/scripts/generate-from-source \
  -H "Content-Type: application/json" \
  -d '{
    "project_title": "测试短剧：旧楼灯火",
    "source_mode": "idea",
    "idea_text": "一个年轻短剧编剧离开城市三年后回到即将拆迁的旧楼，发现父亲生前留下的一份未完成剧本，竟然预告了公司新项目被盗的真相。",
    "target_episode_count": 3,
    "genre": "都市职场",
    "style": "家庭悬疑、快节奏、强反转",
    "extra_requirements": "每集结尾有强钩子，对白自然，冲突快。",
    "language": "zh",
    "ai_options": {
      "provider": "deepseek",
      "model": "deepseek-chat",
      "language": "zh",
      "purpose": "script_generation"
    },
    "metadata": {
      "test_case": "real_llm_quality_acceptance_safe_sample"
    }
  }'
```

记录时只保留响应摘要，不提交完整敏感输出。若输出需要进入文档，只保留结构检查、质量判断和问题描述。

## 8. 记录方式

建议后续新增：

`docs/REAL_LLM_QUALITY_ACCEPTANCE_LOG.md`

每条记录包含：

- 日期；
- provider；
- model；
- source_mode；
- 输入样本摘要；
- 是否成功；
- 是否真实 LLM 模式；
- schema 是否通过；
- 输出质量评价；
- 发现问题；
- 是否需要 prompt 优化；
- 是否可进入前端编辑和导出；
- 安全说明。

建议记录格式：

| Date | Provider | Model | Source Mode | Result | Quality | Issues | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-05-04 | deepseek | deepseek-chat | idea | pass | usable | none | keep prompt |

不记录 API Key，不记录 `.env`，不记录真实客户内容。

## 9. 失败处理

常见失败类型：

- API Key 缺失；
- provider / base_url / model 配置错误；
- timeout；
- 外部 provider 返回非 200；
- 模型返回空内容；
- 模型返回非 JSON；
- JSON 可解析但不符合 `ShortDramaScriptOutput`；
- 输出字段缺失；
- 输出质量明显不可用；
- 前端错误提示暴露本地地址或技术细节。

处理原则：

- 配置错误先检查 `LLM_SETUP.md` 和 provider-aware `llm_enabled`；
- timeout 先降低样本长度或调整请求超时，不直接扩大调用规模；
- JSON 解析失败优先优化 prompt 和 parser 容错；
- schema 失败必须记录具体缺失字段；
- 输出质量问题应进入 prompt 优化，不应靠前端硬修；
- 前端错误提示应产品化，例如“生成失败，请稍后重试或联系技术支持。”；
- 任何失败记录都不得包含 API Key、真实剧本或本机绝对路径。

## 10. 后续小步建议

- 第 288 步：新增真实 LLM 验收日志模板；
- 第 289 步：DeepSeek 三入口小样本验收；
- 第 290 步：根据 DeepSeek 输出优化 prompt；
- 第 291 步：Mimo / Kimi / MiniMax 抽检计划或可选验收；
- 第 292 步：更新 README / LLM_SETUP 中真实模型验收状态。

当前结论：

Dramora 已具备三入口真实模型调用、在线编辑和导出闭环。服务器购买前的下一项关键工作不是继续堆新功能，而是用安全虚构样本对真实模型输出质量、错误处理和前端闭环做可记录、可复查的验收。
