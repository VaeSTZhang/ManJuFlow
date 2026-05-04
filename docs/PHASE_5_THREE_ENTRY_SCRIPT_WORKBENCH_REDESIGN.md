# Phase 5 Three-entry Script Workbench Redesign｜三入口短剧剧本工作台重整方案

> 当前状态：老板已取消当前版本的右侧 AI 聊天界面、AI Assistant、`/api/assistant/chat` 和 `suggested_actions`。本文中关于后续 Assistant 右侧面板的内容仅作为历史方案归档，不纳入当前实施路线。三入口工作台继续聚焦剧本生成 / 改编、在线编辑、导入导出、用量记录、质量评审和后续分镜 / Prompt 工作流。

## 1. 需求变化说明

本次需求变化明确了第五阶段的产品重心：

- 当前老板 / 用户更关注短剧剧本生成与改编；
- 后续文生图、文生视频暂不考虑；
- 剧本切分到分镜 / Prompt 暂时作为下一大功能预备；
- 当前主产品应聚焦三种来源生成短剧剧本。

因此，第五阶段不应继续把“已有剧本切分到 Prompt”作为主入口第一优先级，也不应过早把产品重心转向图片或视频生成。现阶段应先把短剧剧本生成与改编工作台做清楚、做稳定、做得适合市场试用。

## 2. 新的产品定位

ManJuFlow 当前阶段建议定位为：

> 面向编剧、短剧策划、漫剧内容团队的 AI 短剧剧本生成与改编工作台。

核心不是单纯聊天，也不是图片生成，而是：

- 从灵感生成短剧剧本；
- 从电影剧本改编短剧剧本；
- 从小说改编短剧剧本；
- 支持在线编辑、导出、上传；
- 后续可继续切分到分镜 / Prompt。

这意味着 ManJuFlow 的第五阶段市场试用目标，应从“完整媒体生成链路展示”调整为“短剧文字内容生产工作台可用”。

## 3. 三个主入口

### 入口 A：灵感到短剧剧本

适用用户：

- 想从一句创意开始；
- 想快速生成短剧大纲、人物和分集剧本；
- 没有现成剧本，但有题材、人物或爽点方向。

输入建议：

- `idea_text`；
- `genre`；
- `episode_count`；
- `style`；
- `target_audience`；
- `duration_per_episode`；
- `extra_requirements`。

输出：

- `ShortDramaScriptOutput`。

该入口可以继续复用当前 `Idea → Script` 主链路，但 UI 文案和输出结构需要更明确地服务“短剧剧本”。

### 入口 B：电影剧本改编到短剧剧本

适用用户：

- 有已有电影剧本；
- 有长剧本、影视剧本、分场文本；
- 想改成短剧节奏。

输入建议：

- `source_script_text`；
- `source_type = film_script`；
- `adaptation_goal`；
- `target_episode_count`；
- `short_drama_style`；
- `keep_or_change_characters`；
- `key_plot_must_keep`；
- `extra_requirements`。

输出：

- `ShortDramaAdaptationOutput` 或 `ShortDramaScriptOutput`。

输出应强调：

- 改编策略；
- 删减策略；
- 短剧钩子；
- 分集节奏；
- 保留 / 调整的关键人物和剧情。

电影剧本改短剧不是简单压缩文本，而是需要重构节奏、冲突和每集结尾钩子。

### 入口 C：小说改编到短剧剧本

适用用户：

- 有小说、网文、故事文本；
- 想改成短剧剧本；
- 需要把叙事文本转成场景、对白、冲突和分集结构。

输入建议：

- `novel_text`；
- `source_type = novel`；
- `adaptation_goal`；
- `target_episode_count`；
- `main_characters`；
- `key_relationships`；
- `style`；
- `extra_requirements`。

输出：

- `NovelToShortDramaOutput` 或 `ShortDramaScriptOutput`。

输出应强调：

- 人物关系；
- 剧情主线；
- 冲突改编；
- 分集钩子；
- 从叙事文本到剧本场景的转换。

小说改短剧需要重点解决“叙事描述如何转成可拍、可演、可分镜的剧本内容”。

## 4. 统一输出方向

三种入口最终都应汇入统一的短剧剧本输出协议，例如：

`ShortDramaScriptOutput`

建议包含：

- `project_title`；
- `source_mode`；
- `logline`；
- `world_setting`；
- `characters`；
- `adaptation_notes`；
- `episode_count`；
- `episodes`；
- `metadata`。

`episodes` 建议包含：

- `episode_number`；
- `title`；
- `summary`；
- `hook`；
- `scenes`。

`scenes` 建议包含：

- `scene_number`；
- `location`；
- `time`；
- `description`；
- `dialogues`；
- `visual_notes`；
- `emotion_curve`。

说明：

- 现有 `ScriptOutput` 可以复用或扩展；
- 不应盲目重复造一套完全平行的 schema，避免后续 Storyboard / Prompt 链路混乱；
- 如果新增 `ShortDramaScriptOutput`，需要明确它和现有 `ScriptOutput` 的兼容关系。

## 5. 与现有能力的关系

当前项目已有能力包括：

- Idea → Script；
- Existing Script Segmentation；
- Storyboard；
- ImagePrompt；
- ImageGeneration mock；
- Upload mock；
- Document Export Schema；
- 输入限制；
- 错误提示。

新的三入口设计不是废弃这些能力，而是重排产品入口：

- 灵感入口继续复用现有 `/api/scripts/generate`；
- 电影剧本改编可以复用 script generation service 的 LLMClient，但应使用独立 prompt / schema；
- 小说改编也应使用独立 prompt / schema；
- Script Segmentation 暂时退到“下一步功能”或“生成短剧剧本后继续处理”入口；
- Prompt 生成作为后续阶段能力保留。

换句话说，现有能力仍然是工程基础，但产品主路径需要重新组织为“先生成或改编短剧剧本，再进入后续切分 / 分镜 / Prompt”。

## 6. 前端页面重设计

未来页面流程建议：

1. 内部账户登录；
2. 进入工作台；
3. 弹出或展示“选择创作方式”窗口；
4. 三个创作入口卡片：
   - 灵感生成短剧；
   - 电影剧本改编短剧；
   - 小说改编短剧；
5. 用户选择后进入对应表单；
6. 生成短剧剧本；
7. 在线编辑；
8. 下载 / 导出；
9. 后续可选择进入“切分到分镜 / Prompt”。

设计原则：

- 不要一打开就堆所有 workspace；
- 三入口要让非技术用户一眼看懂；
- Sidebar 可以保留，但主引导应以入口选择为核心；
- 生成结果页应突出短剧剧本内容，而不是 Prompt 或图片；
- 后续再加入 Assistant 右侧面板，辅助用户改写和确认。

建议入口卡片文案：

- 灵感生成短剧：从一句创意开始生成短剧剧本；
- 电影剧本改短剧：将已有电影 / 长剧本改编为短剧节奏；
- 小说改短剧：将小说 / 网文改编为短剧剧本。

## 7. 后端模块建议

后续可新增或调整以下模块。

schemas：

- `short_drama_workbench.py`；
- `adaptation.py` 或 `source_adaptation.py`。

services：

- `idea_to_short_drama_service.py`，或继续复用 `script_service.py`；
- `film_script_adaptation_service.py`；
- `novel_adaptation_service.py`。

prompts：

- `idea_to_short_drama_script_v1.md`，可复用现有 `idea_to_script_v1.md`；
- `film_script_to_short_drama_v1.md`；
- `novel_to_short_drama_v1.md`。

routers：

- 短期可以继续复用 `/api/scripts/generate`；
- 后续可新增：
  - `POST /api/scripts/adapt-film`；
  - `POST /api/scripts/adapt-novel`；
- 或统一为：
  - `POST /api/scripts/generate-from-source`。

### API 设计选择分析

方案 A：拆分 endpoint

- `/api/scripts/generate`；
- `/api/scripts/adapt-film`；
- `/api/scripts/adapt-novel`。

优点：

- 语义清晰；
- 每个入口输入字段更明确；
- 测试和文档更容易分别覆盖。

缺点：

- endpoint 数量增加；
- 前端需要维护多个 API 调用。

方案 B：统一 endpoint

- `/api/scripts/generate-from-source`。

通过 `source_mode` 区分：

- `idea`；
- `film_script`；
- `novel`。

优点：

- 前端入口统一；
- 便于统一追踪项目和 UsageLedger；
- 输出协议更容易统一。

缺点：

- 输入字段会更复杂；
- validation 需要区分不同 source_mode；
- prompt 选择逻辑需要更谨慎。

建议：

- 早期 mock 阶段可以先拆分，保证清晰；
- 产品稳定后再评估是否统一为 `generate-from-source`。

## 8. Mock 与 LLM 策略

策略原则：

- mock 仍用于测试；
- 产品化必须接真实 LLM；
- 三个入口应都支持 mock / llm；
- LLM provider 可以统一使用 DeepSeek 作为低成本主力；
- 但不同入口应有独立 prompt 和清晰 `source_mode`；
- 不能让电影剧本改编和小说改编混用同一个提示词导致输出失控。

建议：

- `source_mode=idea` 使用灵感生成短剧 prompt；
- `source_mode=film_script` 使用电影剧本改短剧 prompt；
- `source_mode=novel` 使用小说改短剧 prompt；
- metadata 中记录 provider、model、source_mode、generation_mode。

## 9. 输入上限与长文本策略

输入限制建议：

- 灵感入口：5,000 字符；
- 电影剧本文本：第一版 UI 上限 100,000 字符；
- 小说文本：第一版 UI 上限 100,000 字符；
- `extra_requirements`：2,000 字符。

说明：

- 100,000 字符不是单次 LLM 调用上限；
- 电影剧本 / 小说改编必须考虑 chunking；
- 长文本需要先摘要 / 拆段 / 提炼人物关系；
- 市场试用版可以先限制文本长度，并提示用户分段上传；
- 后端必须强校验，不能只靠前端提示。

长文本改编建议流程：

文本输入 / 上传
→ 长度校验
→ 分块
→ 章节 / 场景 / 人物关系提炼
→ 改编策略生成
→ 短剧分集结构
→ 每集剧本生成。

## 10. 文档往返关系

三种入口生成后都应支持文档往返：

- 在线编辑；
- 下载 Word；
- 离线修改后上传；
- 上传后重新生成或继续进入下一步；
- 导出 JSON / TXT / DOCX。

`DOCUMENT_ROUND_TRIP_PLAN.md` 继续保留，并应服务新的三入口短剧剧本工作台。

建议：

- 灵感生成短剧结果可下载；
- 电影剧本改编结果可下载；
- 小说改编结果可下载；
- 用户上传修改版后，可重新进入相同入口或进入下一步切分。

## 11. 下一大功能预备：短剧剧本切分到提示词

当前不把切分到 Prompt 作为主入口，但要保留作为后续大功能：

`ShortDramaScriptOutput`
→ `Script Segmentation`
→ `Storyboard`
→ `ImagePrompt`
→ `Media Prompt / ImageGeneration mock`

前端可以在短剧剧本生成结果页提供：

- 继续进入分镜；
- 继续进入 Prompt；
- 导出剧本；
- 在线编辑。

但这些后续按钮不应喧宾夺主。当前主任务是让用户先完成短剧剧本生成或改编。

## 12. 市场试用版完成标准调整

市场试用版必须完成：

- 内部账号 / mock login 入口；
- 三入口选择页面；
- 灵感生成短剧；
- 电影剧本改编短剧；
- 小说改编短剧；
- 字数上限提示；
- 真实 LLM 模式；
- 在线编辑；
- 导出；
- 基础上传；
- 老板演示脚本更新。

暂不必须：

- 真实文生图；
- 真实文生视频；
- 自动成片；
- 复杂多租户；
- 高并发 SaaS；
- 完整版本管理。

这一定义更符合当前老板侧目标：先投入给编剧行业做 AI 文字内容创作赋能，而不是先追求完整媒体生成系统。

## 13. 后续实施路线建议

建议按小闭环推进：

- 第 181 步：三入口工作台重整文档；
- 第 182 步：更新 `MARKET_TRIAL_READINESS_PLAN`；
- 第 183 步：更新 `BOSS_DEMO_SCRIPT`；
- 第 184 步：设计三入口 Schema；
- 第 185 步：设计前端入口选择 UI；
- 第 186 步：新增电影剧本改编 prompt；
- 第 187 步：新增小说改编 prompt；
- 第 188 步：电影剧本改编 mock service；
- 第 189 步：小说改编 mock service；
- 第 190 步：对应 endpoint；
- 第 191 步：前端三入口选择；
- 第 192 步：前端电影剧本改编表单；
- 第 193 步：前端小说改编表单；
- 第 194 步：真实 LLM 接入；
- 第 195 步：浏览器验收；
- 第 196 步：再回到 Document Export / Word 下载。

在完成三入口主产品前，不建议继续深入真实图片生成或视频生成。

## 14. 风险与边界

需要提前明确的风险：

- 电影剧本和小说可能涉及版权；
- 真实用户上传内容不能进入公开仓库；
- 改编输出必须允许人工确认；
- LLM 可能漏保留关键剧情；
- 长文本需要 chunking；
- 不能承诺法律意义上的版权合规判断；
- 对外只能作为技术 / 商务边界建议，不冒充律师结论。

风险控制建议：

- 市场试用只用用户自有或授权文本；
- 对上传内容给出隐私和版权提示；
- 改编结果默认需要人工审核；
- 不在公开仓库保存真实剧本；
- 日志不打印完整输入；
- 长文本改编先做摘要和分块策略。

## 15. 第 181 步验收标准

- `docs/PHASE_5_THREE_ENTRY_SCRIPT_WORKBENCH_REDESIGN.md` 已新增；
- 文档明确三入口；
- 文档明确页面需要先登录再选择创作方式；
- 文档明确小说改短剧；
- 文档明确电影剧本改短剧；
- 文档明确切分到 Prompt 是下一大功能预备；
- 文档明确当前产品化优先级；
- 文档不包含敏感信息；
- 不修改代码。
