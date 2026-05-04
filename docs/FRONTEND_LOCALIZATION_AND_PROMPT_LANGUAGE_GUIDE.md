# Frontend Localization and Prompt Language Guide｜前端中文化与 Prompt 双语输出规范

> 当前状态：老板已取消当前版本的右侧 AI 聊天界面、AI Assistant、`/api/assistant/chat` 和 `suggested_actions`。本文中关于 Assistant Panel 的文案规范仅作为历史方案归档，不纳入当前实施路线。

## 1. 设计目标

ManJuFlow 面向非技术内容生产人员，包括编剧、导演、美术、制片、运营和项目评审人员。前端 UI 应默认中文化，减少英文技术词对使用体验的干扰，降低团队协作门槛。

Prompt 输出内容与 AI 绘图、模型生态和外部工具兼容有关，因此 Prompt 正文允许中文 / 英文切换。UI 本身保持中文，Prompt 语言作为明确选项提供给用户。

## 2. UI 默认中文原则

以下内容应默认使用中文：

- 页面标题；
- workspace 名称；
- Sidebar 文案；
- 按钮；
- 表单 label；
- placeholder；
- 下拉选项；
- Toast；
- 错误提示；
- 空状态提示；
- 操作说明。

原则是：非技术用户在不理解 API、provider、schema 等概念的情况下，也能完成灵感创作、已有剧本导入、分镜生成、绘图 Prompt、图片生成 mock、资产与任务查看。

## 3. 可以保留英文的内容

以下内容可以保留英文：

- JSON 字段名；
- API path；
- provider / model 品牌名，例如 DeepSeek、Kimi、MiniMax；
- `prompt_id`、`shot_id`、`task_id` 等技术标识；
- AI 绘图 Prompt 正文；
- 正向 Prompt / 反向 Prompt 内的英文词组；
- 导出的原始 JSON。

这些英文内容属于数据协议、品牌名、模型输入或调试信息，不要求强行翻译。

## 4. Prompt 输出语言选择

绘图 Prompt 生成应提供两种输出语言：

- 中文；
- 英文。

前端展示中文选项，后端传值保持稳定：

- 中文 -> `zh`
- 英文 -> `en`

默认建议：

- 如果面向 AI 绘图工具，默认英文；
- 如果面向中文团队审稿，允许切换为中文；
- UI 中应说明：英文 Prompt 通常更适合部分绘图模型，中文 Prompt 更方便内部审阅。

## 5. 下拉选项规范

下拉选项应优先展示中文，内部 value 保持稳定。

示例：

- 目标模型：通用模型 / Flux / SDXL / 自定义
- 输出语言：中文 / 英文
- 画幅比例：竖屏 9:16 / 横屏 16:9 / 方图 1:1
- 风格预设：电影写实 / 国漫风 / 写实商业广告 / 暗黑悬疑

内部 value 可保持：

- `general`
- `flux`
- `sdxl`
- `zh`
- `en`
- `cinematic_realistic`

这样既能保证用户看到中文，也能避免破坏前后端数据协议。

## 6. 错误提示规范

错误提示应给用户可操作建议，而不是只显示技术错误。

不推荐：

```text
Request failed
```

推荐：

```text
生成失败，请检查输入内容后重试。如果多次失败，请切换 mock 模式或联系技术人员。
```

常见提示应包含：

- 发生了什么；
- 用户能做什么；
- 是否需要检查后端服务；
- 是否可以切换 mock 模式；
- 是否需要联系技术人员。

## 7. Assistant Panel 文案规范

AI Assistant 面板也应默认中文化：

- 输入框 placeholder 使用中文；
- suggested actions 使用中文；
- Toast 和错误提示使用中文；
- 回复中可以包含少量英文 Prompt 或字段名；
- 不向非技术用户暴露 provider 配置细节。

Assistant 可以在需要时生成英文 Prompt，但交互说明、按钮和建议动作应保持中文。

## 8. 后续落地步骤

建议按小闭环逐步落地：

1. 先完成本文档；
2. 检查当前页面英文文案；
3. 逐步替换 Sidebar / 按钮 / 表单 / 下拉；
4. 单独优化 Prompt language selector；
5. 保持 JSON 字段名和 provider / model 品牌名稳定；
6. 不一次性引入 i18n 框架；
7. 等产品稳定后，再考虑多语言 UI。

## 9. 验收标准

第 157.1 步验收标准：

- `docs/FRONTEND_LOCALIZATION_AND_PROMPT_LANGUAGE_GUIDE.md` 已新增；
- 文档明确 UI 默认中文；
- 文档明确 Prompt 支持中文 / 英文；
- 文档明确哪些英文可保留；
- 文档包含下拉选项中文展示、内部 value 保持稳定的规则；
- 不修改代码；
- 不引入依赖。
