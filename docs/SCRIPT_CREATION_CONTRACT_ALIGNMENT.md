# Script Creation Contract Alignment｜剧本创作前后端契约对齐

## 1. 目标

本文件用于对齐 Dramora｜剧作工坊 剧本创作三入口的前端草稿字段、后端请求字段和统一结果字段。

当前目标是为下一步前端调用 `POST /api/scripts/generate-from-source` 做准备。本文件只做契约审计和映射说明，不接真实后端接口，不调用 DeepSeek，不新增 LLM 调用。

## 2. 当前三入口

- `idea`：灵感生成短剧剧本；
- `film_script`：电影剧本改编短剧本；
- `novel`：小说 / 网文改编短剧本。

后端 `ScriptSourceMode` 还包含：

- `assistant_rewrite`：后续 AI 编剧助手模块使用；
- `uploaded_document`：后续文档导入闭环使用。

当前三入口只覆盖 `idea` / `film_script` / `novel`。

## 3. 前端草稿字段

当前前端草稿字段来自 `apps/web/src/components/creation/CreationHome.tsx`。

### idea

当前 `IdeaCreationDraft` 字段：

- `projectTitle`
- `ideaText`
- `genreStyle`
- `episodeCount`
- `extraRequirements`

对应业务含义：

- `projectTitle`：项目标题；
- `ideaText`：灵感内容；
- `genreStyle`：类型 / 风格；
- `episodeCount`：目标集数；
- `extraRequirements`：额外要求。

### film

当前 `AdaptationDraft` 字段：

- `projectTitle`
- `sourceTitle`
- `sourceText`
- `focus`
- `episodeCount`
- `extraRequirements`

对应业务含义：

- `projectTitle`：项目标题；
- `sourceTitle`：原片 / 原剧本标题；
- `sourceText`：剧本内容；
- `focus`：改编重点；
- `episodeCount`：目标集数；
- `extraRequirements`：额外要求。

### novel

当前 `AdaptationDraft` 字段：

- `projectTitle`
- `sourceTitle`
- `sourceText`
- `focus`
- `episodeCount`
- `extraRequirements`

对应业务含义：

- `projectTitle`：项目标题；
- `sourceTitle`：原小说 / 文本标题；
- `sourceText`：小说 / 网文内容；
- `focus`：人物与剧情改编重点；
- `episodeCount`：目标集数；
- `extraRequirements`：额外要求。

## 4. 后端请求字段

后端请求字段来自 `apps/api/app/schemas/script_generation.py` 中的 `ShortDramaGenerationInput`，当前实际字段如下：

- `project_title: str | None`
- `source_mode: ScriptSourceMode`
- `idea_text: str | None`
- `source_text: str | None`
- `target_episode_count: int`
- `genre: str`
- `style: str`
- `target_audience: str | None`
- `duration_per_episode: str | None`
- `adaptation_goal: str | None`
- `key_plot_must_keep: str | None`
- `main_characters: str | None`
- `key_relationships: str | None`
- `extra_requirements: str | None`
- `language: str`
- `workspace_id: str | None`
- `project_id: str | None`
- `session_id: str | None`
- `user_id: str | None`
- `metadata: dict[str, Any]`

当前后端路由：

- `POST /api/scripts/generate-from-source`
- request model：`ShortDramaGenerationInput`
- response model：`ShortDramaScriptOutput`

当前后端 mock service 已支持：

- `source_mode="idea"`
- `source_mode="film_script"`
- `source_mode="novel"`

当前后端 mock service 会拒绝：

- `source_mode="assistant_rewrite"`
- `source_mode="uploaded_document"`

## 5. 字段映射表

| 前端字段 | 后端字段 | 入口 | 备注 |
| --- | --- | --- | --- |
| `projectTitle` | `project_title` | `idea` / `film_script` / `novel` | 直接映射。 |
| 固定值 `"idea"` | `source_mode` | `idea` | 灵感生成入口。 |
| 固定值 `"film_script"` | `source_mode` | `film` | 电影剧本改编入口。 |
| 固定值 `"novel"` | `source_mode` | `novel` | 小说 / 网文改编入口。 |
| `ideaText` | `idea_text` | `idea` | `source_mode="idea"` 时必须提供。 |
| `sourceText` | `source_text` | `film_script` / `novel` | 改编入口的来源文本。 |
| `episodeCount` | `target_episode_count` | `idea` / `film_script` / `novel` | 后端范围为 1-100；前端下一步构造请求时应保底为正整数。 |
| `genreStyle` | `genre` / `style` | `idea` | 当前前端把类型和风格放在一个字段；下一步请求构造器可先同时映射到 `genre` 和 `style`，后续再考虑拆成两个输入。 |
| `focus` | `adaptation_goal` | `film_script` / `novel` | 改编重点应映射为后端改编目标。 |
| `sourceTitle` | `metadata.source_title` | `film_script` / `novel` | 后端当前没有独立 `source_title` 字段，建议通过 `metadata` 传入。 |
| `extraRequirements` | `extra_requirements` | `idea` / `film_script` / `novel` | 直接映射。 |
| 默认 `"zh"` | `language` | `idea` / `film_script` / `novel` | 当前 UI 中文优先，默认中文。 |
| 当前无显式字段 | `target_audience` | `idea` / `film_script` / `novel` | 可先留空，后续如果 UI 增加受众输入再映射。 |
| 当前无显式字段 | `duration_per_episode` | `idea` / `film_script` / `novel` | 可先留空，后续如需短剧时长控制再补 UI。 |
| 当前无显式字段 | `key_plot_must_keep` | `film_script` / `novel` | 可从 `focus` 或后续独立字段扩展，不建议当前强塞。 |
| 当前无显式字段 | `main_characters` | `idea` / `film_script` / `novel` | 可后续扩展人物输入。 |
| 当前无显式字段 | `key_relationships` | `idea` / `film_script` / `novel` | 可后续扩展关系输入。 |
| `selectedCreativeModel.provider` | 后续 `AIRequestOptions.provider` 或请求级模型覆盖 | `idea` / `film_script` / `novel` | 后端 `ShortDramaGenerationInput` 当前没有 provider 字段；不建议直接塞散字段。 |
| `selectedCreativeModel.model` | 后续 `AIRequestOptions.model` 或请求级模型覆盖 | `idea` / `film_script` / `novel` | 下一阶段应统一模型选项，不要每个功能各写一套。 |

关于 provider / model：

- 当前前端 `CreativeModelPanel` 已有统一选择状态；
- 当前后端 `ShortDramaGenerationInput` 尚未定义 `provider` / `model` / `AIRequestOptions`；
- 下一步如果只是调用现有 mock endpoint，可以暂不传 provider / model；
- 第 217 步再设计请求级模型覆盖，建议统一为 `AIRequestOptions`，而不是在每个业务输入里复制一组模型字段；
- 临时过渡也可以放入 `metadata.creative_model`，但这不应成为长期契约。

## 6. 统一结果字段

统一结果字段来自后端 `ShortDramaScriptOutput`，前端 `apps/web/src/types/scriptGeneration.ts` 已有对应类型。

关键字段：

- `project_title`
- `source_mode`
- `logline`
- `world_setting`
- `characters`
- `adaptation_notes`
- `episode_count`
- `episodes`
- `metadata`

`characters` 和 `episodes` 复用既有剧本结构：

- `CharacterProfile`
- `EpisodeScript`
- `SceneScript`
- `DialogueLine`

前端 `ShortDramaScriptResult` 已经用于承载统一结果，当前可以展示：

- 项目标题；
- 来源入口；
- 使用模型；
- 生成时间；
- 故事梗概；
- 世界观 / 故事背景；
- 主要人物；
- 改编策略、保留元素、调整内容、短剧钩子 / 爆点、备注；
- 分集内容；
- 每集场景；
- 对白。

## 7. 与后续分镜 / Prompt 工作流的关系

Dramora 当前第一主线是剧本创作生成 / 剧本改编。

剧本生成后，后续第二大功能是进入：

```text
短剧剧本 -> 分镜 -> Prompt
```

边界原则：

- 不应把分镜 / Prompt 逻辑塞进 `CreationHome`；
- `CreationHome` 负责三入口草稿、模型选择和生成短剧剧本结果；
- 后续应通过明确按钮或状态 payload 将 `ShortDramaScriptOutput` 带入分镜 / Prompt 工作区；
- 该 payload 应包含 `project_title`、`source_mode`、`episodes`、`characters`、`logline`、`world_setting` 和必要 metadata；
- 分镜工作区再负责把短剧剧本转换为 `StoryboardInput`；
- Prompt 工作区继续消费分镜结果，而不是直接依赖 CreationHome 内部状态；
- AI 模型选择应复用 `CreativeModelPanel` 或统一 `AIRequestOptions`，不要在剧本生成、分镜、Prompt、Assistant、质量评审里各写一套模型选择。

## 8. 当前发现的问题

当前没有阻断前端调用 `POST /api/scripts/generate-from-source` 的契约问题。

已确认一致的部分：

- 前后端都有 `ScriptSourceMode`；
- 前后端都有 `ShortDramaGenerationInput`；
- 前后端都有 `ShortDramaScriptOutput`；
- 三入口 `idea` / `film_script` / `novel` 在后端 mock endpoint 中均已支持；
- 前端 `ShortDramaScriptResult` 已能展示统一结果。

需要下一步处理的非阻断问题：

- `genreStyle` 是前端合并字段，后端是 `genre` + `style` 两个字段。下一步请求构造器应先同时映射，后续再考虑 UI 拆分；
- `sourceTitle` 后端没有独立字段，建议放入 `metadata.source_title`；
- `focus` 应映射到 `adaptation_goal`；
- provider / model 当前不在 `ShortDramaGenerationInput` 中。第 217 步应设计统一 `AIRequestOptions` 或请求级模型覆盖；
- `apps/web/src/api/scriptGeneration.ts` 已有 `generateShortDramaScript` 封装，但 `CreationHome` 当前仍只生成前端本地演示结果，尚未调用该 API。

## 9. 下一步建议

- 第 215 步：前端三入口请求构造器；
- 第 216 步：三入口调用 `generate-from-source` mock；
- 第 217 步：请求携带 provider / model；
- 第 218 步：真实 DeepSeek 小样本验收；
- 第 219 步：短剧剧本结果带入分镜 / Prompt 的 payload 设计。
