# Short Drama Online Editing Milestone Review｜短剧剧本在线编辑阶段复查

## 1. 当前已完成能力

Dramora 在线编辑第一版主干已经完成，当前能力覆盖：

- 基础信息编辑：
  - `project_title`
  - `logline`
  - `world_setting`
- 角色基础字段编辑：
  - `characters[].name`
  - `characters[].role`
  - `characters[].age`
  - `characters[].personality`
  - `characters[].arc`
- 分集基础字段编辑：
  - `episodes[].title`
  - `episodes[].summary`
  - `episodes[].hook`
- `effectiveScript` 数据流：
  - `generatedScript` 保留 AI 原始结果；
  - `editableScript` 保存用户当前编辑稿；
  - 导出和后续工作流默认使用 `editableScript ?? generatedScript`。
- 导出行为：
  - 复制 JSON 使用当前有效稿；
  - 下载 TXT 使用当前有效稿；
  - Word 导出保持后续真实接入状态。
- e2e 覆盖：
  - 基础信息编辑后页面展示；
  - 基础信息编辑后复制 JSON / 下载 TXT；
  - 角色字段编辑后复制 JSON / 下载 TXT；
  - 分集字段编辑后复制 JSON / 下载 TXT；
  - 页面不出现开发态文案；
  - 创作模型切换请求 payload 覆盖 DeepSeek / Mimo / Kimi / MiniMax。
- 组件拆分：
  - `ShortDramaBasicInfoEditor`
  - `ShortDramaCharacterEditor`
  - `ShortDramaEpisodeEditor`
  - `ShortDramaScriptResult` 保留为结果区编排组件；
  - `useShortDramaEditing` 统一管理编辑状态和字段更新。

## 2. 当前未做能力

当前在线编辑第一版明确未做：

- `scenes` 编辑；
- `dialogues` 编辑；
- 新增 / 删除 / 排序角色；
- 新增 / 删除 / 排序分集；
- 修改 `episode_number`；
- 修改 `episode_count`；
- 富文本编辑器；
- 自动保存；
- 服务端保存；
- 数据库持久化；
- 真实 Word 导出；
- 质量评审；
- 局部 LLM 改写按钮；
- 右侧聊天式 AI Assistant、AssistantPanel、`/api/assistant/chat` 或 `suggested_actions`。

这些能力不应混入当前已完成的在线编辑第一版主干，后续需要分别设计小闭环。

## 3. 是否继续做 scenes / dialogues 编辑

建议结论：第一版暂缓 `scenes` / `dialogues` 深层编辑。

理由：

- 深层编辑复杂度明显高于基础字段、角色字段和分集字段；
- `scenes` 会影响后续分镜 / Prompt 的转换质量和 payload 边界；
- `dialogues` 涉及逐句编辑、角色引用、语气统一和场景节奏，不适合在当前阶段仓促打开；
- 当前基础信息、人物和分集字段已经覆盖大部分内部审看修改需求；
- 服务器购买前更紧急的是导出闭环、真实模型质量验收、用量记录和部署前安全；
- 继续深挖 scenes / dialogues 容易让 `ShortDramaScriptResult`、`useShortDramaEditing` 和 e2e 文件继续膨胀。

如果后续确实需要进入深层编辑，应先新增单独设计文档，并拆出 `ShortDramaSceneEditor` / `ShortDramaDialogueEditor`，不能直接堆回现有组件。

## 4. 当前建议下一阶段

建议优先进入：

```text
Document Export / Word 导出闭环
```

理由：

- 老板实操时一定会测试下载；
- 内部用户需要拿到可交付文档；
- 当前 `effectiveScript` 已经准备好，导出可以直接使用当前有效稿；
- JSON / TXT 已经通过 e2e 证明使用编辑稿；
- Word 导出闭环比继续深挖 scenes 编辑更适合当前落地目标；
- 导出闭环完成后，三入口生成、在线编辑和交付文档之间的产品价值更完整。

## 5. 推荐后续步骤

建议后续按以下顺序推进：

1. 第 275 步：Document Export 当前状态审计
2. 第 276 步：Document Export service 支持 current effectiveScript 的 TXT / JSON
3. 第 277 步：DOCX 导出 service
4. 第 278 步：Document Export endpoint
5. 第 279 步：前端 Word 下载接入
6. 第 280 步：e2e 覆盖编辑后 Word / TXT / JSON 导出
7. 第 281 步：再决定是否进入 scenes / dialogues 编辑

说明：

- 如果发现已有 Document Export schema / service，可优先复用；
- 如果缺少 DOCX 依赖，应先做依赖评估，不要直接引入大型库；
- 文档导出不应记录 API Key、本机绝对路径或真实客户剧本到仓库。

## 6. 质量门槛

后续每步必须满足：

- `npm run build` 通过；
- `npm run test:e2e` 通过；
- 后端相关改动必须跑对应 `pytest`；
- 不提交真实剧本、真实电影剧本、真实小说或客户内容；
- 不读取或输出 `.env`；
- 不提交 API Key；
- 不写死本机路径；
- 不引入大型依赖前先评估必要性和替代方案；
- 不让 `ShortDramaScriptResult` 重新膨胀；
- 新增功能优先拆组件 / hook / service，保持边界清晰；
- e2e 继续使用安全虚构样本和 route fulfill，不真实调用外部模型。

## 7. 当前阶段结论

在线编辑第一版主干已可进入导出闭环。

当前结论：

- 基础信息、角色字段、分集字段编辑已经覆盖内部审看第一版的主要需求；
- 复制 JSON / 下载 TXT 已经使用 `effectiveScript`；
- 自动化 e2e 已覆盖编辑后导出使用编辑稿；
- `scenes` / `dialogues` 编辑暂缓，不作为服务器购买前置；
- Document Export / DOCX 是下一优先级。

下一阶段应优先把“生成 → 编辑 → 导出 Word / TXT / JSON”打成完整闭环，再回头评估深层场景和对白编辑。
