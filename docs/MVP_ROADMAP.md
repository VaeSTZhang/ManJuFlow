# Dramora｜剧作工坊 MVP Roadmap

## 当前产品主线

Dramora 当前第五阶段主线已调整为：

```text
内部账号 / mock login
→ 三入口选择
→ 灵感生成短剧剧本 / 电影剧本改短剧 / 小说改短剧
→ 在线编辑 / DOCX 下载 / 上传修改稿
→ 用量记录 / 质量评审
→ 下一大功能：短剧剧本切分 / 分镜 / Prompt
```

当前市场试用重点是 **AI 短剧剧本生成与改编工作台**，不是文生图、文生视频或自动成片。

## 已完成基础能力

- Phase 1：Idea → Script；
- Phase 2：Script → Storyboard；
- Phase 3：Storyboard → ImagePrompt；
- Phase 4：ImagePrompt → ImageGeneration mock / bundle / asset / task / workspace；
- Phase 5 已完成部分：
  - Existing Script Segmentation schema / service / endpoint；
  - 前端已有剧本工作区；
  - mock Word upload；
  - 输入长度限制与前端字数提示；
  - 后端统一输入长度校验；
  - Document Round-trip 方案；
  - Document Export Schema；
  - 三入口短剧工作台重整方案；
  - 三入口项目结构重整方案；
  - 市场试用方案和老板演示脚本已按三入口方向更新。

## P0｜当前优先级

- Three-entry script workbench redesign；
- Idea to short drama script；
- Film script to short drama adaptation；
- Novel to short drama adaptation；
- Entry selection UI after login；
- Editable script result；
- DOCX download；
- Input limits；
- Usage ledger and quality review planning。

中文说明：

- 三入口短剧剧本工作台重整；
- 灵感生成短剧剧本；
- 电影剧本改编短剧剧本；
- 小说改编短剧剧本；
- 登录后的入口选择页；
- 可在线编辑的短剧剧本结果；
- DOCX 下载；
- 输入字数限制；
- 用量记录与质量评审规划。

## P1｜下一阶段能力

- Document round-trip；
- Usage ledger；
- Quality review；
- Script segmentation / storyboard / prompt as next big feature。

中文说明：

- 文档往返：在线编辑、下载 Word、离线修改、再上传；
- 用量记录：记录内部试用中的模型调用和成本线索；
- 质量评审：评估生成剧本的可用性、短剧节奏和改编质量；
- 短剧剧本切分 / 分镜 / Prompt 作为下一大功能。

## P2｜后续媒体生成方向

- Image generation；
- Video generation；
- ComfyUI / GPU deployment。

中文说明：

- 图片生成；
- 视频生成；
- ComfyUI / GPU 私有部署。

这些能力不作为当前市场试用第一重点。进入真实 ComfyUI / GPU 前，必须继续遵守私有部署 checklist 和公开仓库安全边界。

## 当前暂不做

- 真实文生图作为市场试用主功能；
- 文生视频；
- 自动成片；
- 真实 ComfyUI 公共服务；
- 真实 GPU 服务器接入；
- 复杂多租户正式权限系统；
- 高并发 SaaS；
- Redis / Celery / MinIO；
- 复杂多 Agent；
- 右侧 AI 聊天界面 / AI Assistant；
- AssistantPanel、`/api/assistant/chat`、`suggested_actions`；
- Docker 生产部署。

说明：这里取消的是右侧聊天式 AI Assistant，不是取消 Dramora 的核心 LLM 创作能力。Dramora 仍继续通过 DeepSeek / Mimo / Kimi / MiniMax 等模型进行剧本生成、电影剧本改编、小说 / 网文改编、扩写、质量评审和后续分镜 / Prompt 生成。

## 项目推进原则

- 每次只做一个小闭环；
- 不为了赶进度写死结构；
- 三入口通过 `source_mode`、独立 prompt、独立 form、独立 service 边界推进；
- Document import/export 独立于 upload mock；
- 当前版本不规划右侧聊天式 AI Assistant；历史方案仅归档，不进入当前实施路线；
- AI 改写、扩写和质量评审应作为剧本编辑区、质量评审区或局部操作能力接入，而不是作为通用聊天窗口接入；
- 公开仓库不提交 API Key、`.env`、真实客户数据、真实服务器地址、私有 workflow 或模型权重；
- 每个阶段完成后测试、文档、再提交。
