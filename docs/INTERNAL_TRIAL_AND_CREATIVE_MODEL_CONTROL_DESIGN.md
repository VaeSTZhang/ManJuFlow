# Internal Trial and Creative Model Control Design｜内部试用与创作模型控制设计

## 1. 当前产品定位

Dramora｜剧作工坊 当前不做公开商用，短中期面向公司内部 5-10 人稳定使用。

近期目标是稳定支持：

- 灵感生成短剧剧本；
- 电影剧本改编短剧本；
- 小说 / 网文改编短剧本；
- Word 导入；
- Word 导出；
- 基础用量记录；
- 后续人工评审。

当前产品重点是剧本创作生成与文本改编，而不是公开 SaaS、文生视频或大规模媒体生成生产系统。

## 2. 为什么不按公开 SaaS 设计

当前暂不做：

- 公开注册；
- 手机号实名；
- 在线支付；
- 多租户计费；
- 大规模公开访问；
- 复杂营销页；
- GPU / 视频生成生产部署。

当前优先级是内部稳定、权限安全、成本控制、可维护性和技术组可接手。内部长期使用比外部流量增长更重要，系统设计应先保证公司人员能稳定登录、稳定生成、稳定下载、稳定评审。

## 3. 内部账号基本原则

内部账号第一版建议：

- 不强制手机号；
- 不强制实名；
- 支持中文用户名；
- 支持英文用户名；
- 用户自设密码必须包含大写字母、小写字母、数字；
- 建议密码长度不少于 8 位；
- 后续可加入管理员审批、邀请制和禁用账号。

账号体系的目标不是做公开用户增长，而是明确“谁在使用、什么时候使用、生成了什么、用了哪个模型、后续谁评审”。

## 4. 创作模型控制总原则

DeepSeek 是当前内部默认推荐模型，但 DeepSeek 不能写死。

所有 AI 功能都应通过统一模型配置或 AI request options 调用。业务层只关心：

- 剧本生成；
- 文本改编；
- 质量评审。

模型层通过 provider / model 配置选择 DeepSeek、Mimo、Kimi、MiniMax 或未来私有模型。

原则：

- 默认推荐 DeepSeek；
- 保留 Mimo、Kimi、MiniMax 等已配置 provider 的扩展位；
- 后端默认 provider / model 通过 `DEFAULT_LLM_PROVIDER` / `DEFAULT_SCRIPT_MODEL` 配置；
- 不在业务 service 中硬编码具体 provider；
- 请求级 `AIRequestOptions` 应记录本次使用的 provider / model / purpose。

## 5. 统一“创作模型”小窗口设计

前端应提供统一小窗口 / 浮层，而不是在每个功能里重复散落模型选择器。

入口文案建议：

```text
创作模型：DeepSeek
切换
```

窗口内容建议：

- 推荐：DeepSeek；
- 可选：Mimo、Kimi、MiniMax；
- 适用范围：剧本生成、剧本改编、质量评审、后续分镜 / Prompt；
- 输出语言；
- 生成后保留结果；
- 下载 Word；
- 记录本次模型与参数，方便人工评审。

统一入口的目的：

- 避免每个功能页面重复维护模型选项；
- 避免用户不知道当前由哪个模型生成；
- 避免 DeepSeek 被写死；
- 方便未来技术组新增 provider 或切换默认模型；
- 方便人工评审时追溯“这个稿子由哪个模型生成”。

## 6. 建议的前端组件

后续建议新增：

```text
apps/web/src/components/ai/CreativeModelPanel.tsx
```

职责：

- 展示当前创作模型；
- 打开模型选择浮层；
- 选择 provider / model；
- 将选择结果传给剧本生成、文本改编、质量评审和后续分镜 / Prompt；
- 默认 DeepSeek；
- 代码层可保留系统默认配置能力，但普通用户模型卡片不展示“系统默认模型”。

建议状态结构：

```ts
selectedCreativeModel = {
  provider: "deepseek",
  model: "deepseek-chat",
  label: "DeepSeek",
  source: "user_selected" | "system_default",
};
```

组件不应直接承担业务生成逻辑，只负责选择和展示模型配置。

## 7. 建议的后端数据结构

当前已开始落地统一 `AIRequestOptions`：

- provider；
- model；
- temperature；
- max_tokens；
- language；
- purpose。

`purpose` 可包含：

- script_generation；
- film_adaptation；
- novel_adaptation；
- script_rewrite；
- quality_review。

这些字段应进入请求级上下文，不应散落硬编码。业务 service 可以接收 `AIRequestOptions`，再由统一 LLM client / provider adapter 决定具体调用。当前三入口剧本生成请求已开始携带该结构，但真实模型切换仍需后续接入。

## 8. AI 功能覆盖范围

统一模型控制应覆盖：

- 灵感生成短剧剧本；
- 电影剧本改编；
- 小说 / 网文改编；
- 改写选中文本；
- 增强短剧钩子；
- 优化对白；
- 质量评审；
- 后续分镜 / Prompt 生成。

短期优先覆盖三入口剧本生成、文本改编和质量评审，后续再逐步覆盖分镜 / Prompt。

当前版本不规划右侧聊天式 AI Assistant、AssistantPanel、`/api/assistant/chat` 或 `suggested_actions`。历史 Assistant 方案仅作为归档，不进入当前实施路线。

这不代表取消核心 LLM 创作能力。Dramora 仍继续通过 DeepSeek / Mimo / Kimi / MiniMax 等模型进行剧本生成、电影剧本改编、小说 / 网文改编、扩写、质量评审和后续分镜 / Prompt 生成。AI 改写、扩写和质量评审应作为产品化按钮、表单或局部操作能力接入，而不是作为通用聊天窗口接入。

## 9. Word 下载与人工评审

AI 生成内容不直接视为最终稿。

用户应可以下载 `.docx` 文件，在本地或公司内部流程中人工审阅。Word 文件可记录生成信息，例如：

- 产品：Dramora｜剧作工坊；
- 输入方式；
- 使用模型；
- 生成时间；
- 人工审阅提醒。

建议 Word 文件中加入简短说明：

```text
本文件由 Dramora｜剧作工坊生成，内容应由人工审阅后再进入正式交付或生产流程。
```

真实客户剧本、生成稿、审阅稿不进入公开仓库。

## 10. 用量与质量记录

后续应记录：

- user_id；
- project_id / workspace_id；
- provider；
- model；
- purpose；
- input_length；
- output_length；
- success / failure；
- created_at；
- 用户人工评分 / 备注。

第一版可以先记录基础 metadata，后续再扩展质量评分、版本对比、人工审阅意见和模型质量评估。

## 11. 未来技术组扩展边界

该设计应允许未来技术组：

- 新增 provider；
- 替换默认模型；
- 增加企业私有模型；
- 做模型质量对比；
- 按用户 / 项目配置默认模型；
- 将内部使用扩展为商用版本。

这些扩展不应要求重写剧本生成业务逻辑。业务代码只依赖统一模型选项和 request options。

## 12. 后续建议步骤

- 第 205 步：统一 ShortDramaScriptResult 前端展示组件；
- 第 206 步：前端 CreativeModelPanel 组件；
- 第 207 步：把 CreativeModelPanel 接入剧本创作页；
- 第 208 步：三入口请求携带 provider / model；
- 第 209 步：后端 AIRequestOptions / 请求级模型覆盖；
- 第 210 步：DeepSeek 默认模型真实小样本验收；
- 第 211 步：Word 导出附加生成信息；
- 第 212 步：UsageLedger 记录 provider / model / purpose。
