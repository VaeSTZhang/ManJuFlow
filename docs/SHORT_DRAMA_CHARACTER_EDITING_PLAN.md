# Short Drama Character Editing Plan｜短剧角色基础字段编辑计划

## 1. 背景与目标

Dramora 已经支持 `ShortDramaScriptOutput` 的基础信息在线编辑：

- `project_title`
- `logline`
- `world_setting`

下一步需要支持角色基础字段编辑。角色信息是短剧剧本可用性的关键，直接影响人物辨识度、人物弧光、对白方向和后续分镜 / Prompt 工作流。但 `characters` 是数组结构，不能像 `project_title` 这类浅层字段一样直接更新，否则容易让 `ShortDramaScriptResult` 或 `useShortDramaEditing` 继续膨胀。

本计划用于明确角色编辑的第一版边界、状态更新策略、组件拆分方式和 e2e 验收方式。

## 2. 第一版编辑范围

第一版只编辑已有角色字段：

- `name`
- `role`
- `age`
- `personality`
- `arc`

第一版不做：

- 新增角色；
- 删除角色；
- 拖拽排序；
- 角色关系图；
- 头像 / 角色图；
- 服务端保存。

原因：

- 现有 `ShortDramaScriptOutput.characters` 已经能承载基础角色信息；
- 编辑已有字段可以覆盖内部审看和轻量修订需求；
- 增删角色会影响分集、场景、对白引用，必须单独设计一致性策略；
- 拖拽排序、角色关系图和头像属于后续增强，不应阻塞第一版在线编辑闭环。

## 3. 状态更新策略

建议在 `apps/web/src/hooks/creation/useShortDramaEditing.ts` 中新增：

```ts
updateEditableCharacterField(
  characterIndex: number,
  field: keyof CharacterProfile,
  value: string,
): void
```

要求：

- 基于 `editableScript ?? generatedScript` clone；
- 只更新 `characters[characterIndex][field]`；
- 不修改 `generatedScript`；
- 更新后 `setHasUnsavedScriptEdits(true)`；
- 如果 `characterIndex` 不存在，安全返回；
- 不改变 `metadata`；
- 不改变 `episodes`；
- 不改变 `source_mode`；
- 不改变 `episode_count`；
- 不做角色增删和排序。

建议实现方向：

```ts
setEditableScript((currentEditableScript) => {
  const baseScript = currentEditableScript ?? generatedScript;

  if (!baseScript || !baseScript.characters[characterIndex]) {
    return currentEditableScript;
  }

  const nextScript = cloneShortDramaScript(baseScript);
  nextScript.characters[characterIndex] = {
    ...nextScript.characters[characterIndex],
    [field]: value,
  };

  return nextScript;
});
setHasUnsavedScriptEdits(true);
```

该函数只处理角色数组的一层字段更新，不处理深层分集、场景和对白。

## 4. 组件拆分建议

建议新增：

```text
apps/web/src/components/creation/ShortDramaCharacterEditor.tsx
```

组件职责：

- 展示 `characters` 列表；
- `isEditing` 时展示 input / textarea；
- 非编辑状态保持当前展示；
- 不管理状态；
- 不调用 API；
- 不处理保存 / 放弃 / 恢复原稿；
- 通过 `onUpdateCharacterField` 回调更新。

建议 props：

```ts
type ShortDramaCharacterEditorProps = {
  characters: CharacterProfile[];
  canEditFields: boolean;
  onUpdateCharacterField?: (
    characterIndex: number,
    field: keyof CharacterProfile,
    value: string,
  ) => void;
};
```

字段展示建议：

- `name` 使用 input；
- `role` 使用 input；
- `age` 使用 input；
- `personality` 使用 textarea；
- `arc` 使用 textarea；
- 保留现有 `short-script-character-grid` / `short-script-character` 的视觉层级；
- 如需新增样式，优先复用 `short-script-edit-field`。

组件边界：

- `ShortDramaScriptResult` 只负责把 `result.characters`、`canEditFields` 和回调传进去；
- `ShortDramaCharacterEditor` 只负责角色区；
- `useShortDramaEditing` 只负责 immutable update；
- 不把角色编辑逻辑写回 `ShortDramaBasicInfoEditor`。

## 5. e2e 策略

新增或扩展 Playwright 测试：

- 生成安全虚构结果；
- 点击“开始编辑”；
- 修改第一个角色的 `name`；
- 修改第一个角色的 `personality`；
- 修改第一个角色的 `arc`；
- 点击“保存本次修改”；
- 页面显示修改后的角色信息；
- 点击“复制 JSON”；
- clipboard JSON 包含修改后的角色字段；
- 点击“下载 TXT”；
- 下载 TXT 包含修改后的角色字段。

建议测试数据继续使用虚构内容，不使用真实客户剧本、真实电影剧本或真实小说内容。

建议新增稳定 `data-testid`：

- `character-name-editor-0`
- `character-role-editor-0`
- `character-age-editor-0`
- `character-personality-editor-0`
- `character-arc-editor-0`

第一版 e2e 可以只覆盖第一个角色，避免一次性扩大测试复杂度。后续如支持增删角色，再补数组长度和排序相关测试。

## 6. 不做事项

本阶段角色编辑不做：

- 不做增删角色；
- 不做角色排序；
- 不做复杂人物关系；
- 不做富文本；
- 不接数据库；
- 不做服务端保存；
- 不做自动保存；
- 不做 Assistant 自动改角色；
- 不改变后端契约；
- 不改 `ShortDramaScriptOutput` 类型；
- 不让角色编辑影响 `episodes` / `scenes` / `dialogues`；
- 不引入新的状态管理库。

## 7. 分步实施建议

建议后续按小步推进：

1. 第 261 步：`useShortDramaEditing` 增加 `updateEditableCharacterField`
2. 第 262 步：拆 `ShortDramaCharacterEditor` 并支持只读展示不变
3. 第 263 步：开启角色字段编辑
4. 第 264 步：e2e 覆盖角色编辑与导出
5. 第 265 步：结构复查，防止 `ShortDramaScriptResult` 膨胀

每一步都应保持：

- `npm run build` 通过；
- `npm run test:e2e` 通过；
- 不改后端；
- 不改 API；
- 不改 `ShortDramaScriptOutput` 契约；
- 不引入富文本或复杂状态管理；
- `git diff` 范围清晰。
