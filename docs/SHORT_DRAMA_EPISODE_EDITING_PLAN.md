# Short Drama Episode Editing Plan｜短剧分集基础字段编辑计划

## 1. 背景与目标

Dramora 已经支持 `ShortDramaScriptOutput` 的基础信息在线编辑：

- `project_title`
- `logline`
- `world_setting`

也已经支持角色基础字段编辑：

- `characters[].name`
- `characters[].role`
- `characters[].age`
- `characters[].personality`
- `characters[].arc`

下一步需要支持分集基础字段编辑。`episodes` 是短剧成稿的核心内容，直接影响剧本节奏、分集钩子、后续场景拆分、分镜和 Prompt 工作流。但 `episodes` 是数组结构，且每一集下面还有 `scenes` 和 `dialogues`，复杂度明显高于基础信息和角色字段。

本计划用于明确分集编辑第一版边界、状态更新策略、组件拆分方式和 e2e 验收方式，避免一次性打开场景、对白、增删集等高风险能力。

## 2. 第一版编辑范围

第一版只编辑已有 episode 的基础字段：

- `title`
- `summary`
- `hook`

第一版不做：

- 新增集；
- 删除集；
- 重排集；
- 修改 `episode_number`；
- 批量改集数；
- 编辑 `scenes`；
- 编辑 `dialogues`；
- 自动重写全剧结构。

原因：

- `title` / `summary` / `hook` 已能覆盖内部审看和轻量修订需求；
- 新增、删除或重排集会影响 `episode_count`、场景归属和后续分镜，需要单独设计一致性策略；
- `scenes` / `dialogues` 属于更深层编辑能力，应在分集基础字段稳定后再单独拆分；
- 自动重写全剧结构属于 LLM 改写能力，应通过明确按钮或质量评审建议进入，不应混入普通字段编辑。

## 3. 状态更新策略

建议在 `apps/web/src/hooks/creation/useShortDramaEditing.ts` 中新增：

```ts
updateEditableEpisodeField(
  episodeIndex: number,
  field: "title" | "summary" | "hook",
  value: string,
): void
```

要求：

- 基于 `editableScript ?? generatedScript` clone；
- 只更新 `episodes[episodeIndex][field]`；
- 不修改 `generatedScript`；
- 不修改 `characters`；
- 不修改 `metadata`；
- 不修改 `scenes`；
- 不修改 `episode_number`；
- 不修改 `episode_count`；
- 更新后 `setHasUnsavedScriptEdits(true)`；
- 如果 `episodeIndex` 不存在，安全返回。

建议实现方向：

```ts
setEditableScript((currentEditableScript) => {
  const baseScript = currentEditableScript ?? generatedScript;

  if (!baseScript || !baseScript.episodes[episodeIndex]) {
    return currentEditableScript;
  }

  const nextScript = cloneShortDramaScript(baseScript);
  nextScript.episodes[episodeIndex] = {
    ...nextScript.episodes[episodeIndex],
    [field]: value,
  };

  return nextScript;
});
setHasUnsavedScriptEdits(true);
```

该函数只处理分集数组的一层字段更新，不处理场景、对白、增删集和排序。

## 4. 组件拆分建议

建议新增：

```text
apps/web/src/components/creation/ShortDramaEpisodeEditor.tsx
```

组件职责：

- 展示 `episodes` 列表；
- `isEditing` 时编辑 `title` / `summary` / `hook`；
- 非编辑状态保持当前展示；
- 不管理状态；
- 不调用 API；
- 不处理保存 / 放弃 / 恢复原稿；
- 后续 `scenes` 单独拆 `ShortDramaSceneEditor`，不混入本步。

建议 props：

```ts
type ShortDramaEpisodeEditorProps = {
  episodes: EpisodeScript[];
  canEditFields: boolean;
  onUpdateEpisodeField?: (
    episodeIndex: number,
    field: "title" | "summary" | "hook",
    value: string,
  ) => void;
};
```

字段展示建议：

- `title` 使用 input；
- `summary` 使用 textarea；
- `hook` 使用 textarea；
- 保留现有 `short-script-episode` 的视觉层级；
- 如需新增样式，优先复用 `short-script-edit-field`。

组件边界：

- `ShortDramaScriptResult` 只负责把 `result.episodes`、`canEditFields` 和回调传进去；
- `ShortDramaEpisodeEditor` 只负责分集区；
- `useShortDramaEditing` 只负责 immutable update；
- `ShortDramaSceneEditor` 后续再单独设计，不塞进本组件。

## 5. e2e 策略

新增或扩展 Playwright 测试：

- 生成安全虚构结果；
- 点击“开始编辑”；
- 修改第一集 `title`；
- 修改第一集 `summary`；
- 修改第一集 `hook`；
- 点击“保存本次修改”；
- 页面显示修改后的分集字段；
- 点击“复制 JSON”；
- clipboard JSON 包含修改后的分集字段；
- 点击“下载 TXT”；
- 下载 TXT 包含修改后的分集字段。

建议测试数据继续使用虚构内容，不使用真实客户剧本、真实电影剧本或真实小说内容。

建议新增稳定 `data-testid`：

- `episode-title-editor-0`
- `episode-summary-editor-0`
- `episode-hook-editor-0`

第一版 e2e 可以只覆盖第一集，避免一次性扩大测试复杂度。后续如支持增删集或场景编辑，再补数组长度、排序和深层字段相关测试。

## 6. 不做事项

本阶段分集编辑不做：

- 不做增删集；
- 不做重排；
- 不做 `scenes` / `dialogues` 编辑；
- 不做自动重写全剧；
- 不接数据库；
- 不做服务端保存；
- 不做自动保存；
- 不改变后端契约；
- 不改 `ShortDramaScriptOutput` 类型；
- 不修改 `episode_number`；
- 不修改 `episode_count`；
- 不引入富文本编辑器；
- 不引入复杂状态管理。

## 7. 分步实施建议

建议后续按小步推进：

1. 第 270 步：`useShortDramaEditing` 增加 `updateEditableEpisodeField`
2. 第 271 步：拆 `ShortDramaEpisodeEditor` 只读展示
3. 第 272 步：开启 episode `title` / `summary` / `hook` 编辑
4. 第 273 步：e2e 覆盖 episode 编辑与导出
5. 第 274 步：结构复查，决定是否进入 scenes 编辑或先做导出闭环

每一步都应保持：

- `npm run build` 通过；
- `npm run test:e2e` 通过；
- 不改后端；
- 不改 API；
- 不改 `ShortDramaScriptOutput` 契约；
- 不引入富文本或复杂状态管理；
- `git diff` 范围清晰。
