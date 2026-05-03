# Existing Script Workflow Acceptance｜已有剧本工作流验收标准

## 1. 文档目的

本文档用于定义第五阶段“已有剧本输入”主链路的验收标准，确保它达到老板演示和市场试用要求。

该链路是 ManJuFlow 当前市场试用目标中的核心产品能力之一：让编剧、短剧策划和漫剧内容团队可以把已有剧本文字快速拆解为结构化片段，再继续进入分镜和绘图 / 媒体提示词链路。

## 2. 核心链路定义

英文链路：

```text
Existing Script Input
  -> Script Segmentation
  -> Storyboard Generation
  -> Image / Media Prompt Generation
  -> Copy / Export
```

中文链路：

```text
已有剧本输入
  -> 剧本切分
  -> 分镜生成
  -> 绘图 / 媒体提示词生成
  -> 复制 / 导出
```

当前验收重点是文字内容创作和提示词生产，不验收真实文生图、文生视频或真实 ComfyUI / GPU 链路。

## 3. 当前已具备能力

根据当前项目状态，已有剧本工作流已具备：

- 后端 `POST /api/scripts/segment` 已存在；
- Script Segmentation Schema / Service / Endpoint 已完成；
- 前端已有 `ScriptSegmentationWorkspace`；
- 支持粘贴已有剧本文本；
- 支持 mock Word 剧本文档上传；
- `extracted_text` 自动填入切分区；
- 切分结果可复制 / 导出；
- 切分结果可带入分镜生成；
- 分镜可继续进入 ImagePrompt 链路；
- 后端相关测试已覆盖；
- 前端 build 最近通过。

边界说明：

- `/api/uploads/script` 当前仍是 JSON mock metadata-only upload；
- 当前不是真实 multipart 文件上传；
- 当前不读取真实 `.docx` 文件；
- 当前不保存真实上传文件；
- 当前不接真实客户数据。

## 4. 老板演示验收标准

老板演示时必须能完成：

1. 打开网页；
2. 进入“已有剧本” workspace；
3. 粘贴一段安全虚构剧本文本；
4. 点击切分；
5. 页面展示 segments；
6. 点击带入分镜；
7. 页面跳转或切换到分镜区域；
8. 生成 Storyboard；
9. 将 Storyboard 带入绘图 / 媒体 Prompt；
10. 生成 ImagePrompt；
11. 复制 JSON；
12. 导出 JSON。

演示过程必须使用虚构素材，不使用真实客户剧本，不展示 API Key，不展示本机绝对路径，不展示真实服务器信息。

## 5. 市场试用验收标准

市场试用版必须进一步满足：

- 输入区有清晰提示；
- 长文本限制提示清楚；
- mock 上传边界清楚；
- 切分 loading 状态清楚；
- 错误提示清楚；
- segments 展示结构清楚；
- 每个 segment 至少能看出原文、摘要、人物、地点、冲突、情绪、视觉备注；
- 复制 / 导出按钮可用；
- “带入分镜”按钮可用；
- 分镜结果能继续进入 Prompt；
- 不丢失 `project_title`；
- 不串 workspace；
- 不依赖真实客户数据；
- 不展示敏感信息。

市场试用前还应确认浏览器流程在不同输入长度下表现稳定，尤其是空文本、短文本、较长文本、mock 上传后文本覆盖等场景。

## 6. 测试数据建议

浏览器验收建议使用以下安全虚构短剧文本，不使用真实客户数据。

```text
第1集 第1场｜旧电影院｜雨夜。
旧电影院已经停业多年，门口的霓虹灯只剩下半截还在闪。编剧林棠抱着一箱父亲留下的旧剧本，站在售票厅中央。她原本打算把这些稿子全部烧掉，却在最底下发现一本没有结局的剧本。

第1集 第2场｜放映室｜夜。
周砚从放映室里走出来，手里拿着一卷老胶片。
周砚：你父亲当年不是失踪，是有人把最后一幕剪掉了。
林棠：你凭什么这么说？
周砚：因为我看过那一幕。

第1集 第3场｜银幕前｜夜。
放映机突然自己启动，银幕上出现林棠父亲年轻时的影像。影像里的他说：如果你看到这里，说明故事还没有结束。
林棠握紧剧本，决定留下来找出真相。
```

验收时可观察：

- 是否能识别多个场景；
- 是否能保留人物和地点；
- 是否能提取冲突和情绪；
- 是否能生成适合后续分镜的摘要和视觉备注。

## 7. 后端接口验收

后端接口验收方向：

- `POST /api/scripts/segment`
- `POST /api/storyboards/generate`
- `POST /api/prompts/generate`
- `POST /api/uploads/script`

说明：

- `/api/uploads/script` 当前为 mock metadata-only upload；
- 后续真实 `.docx` 上传要单独小闭环实现；
- 当前验收不要求真实 multipart/form-data；
- 当前验收不要求 python-docx；
- 当前验收不要求真实 LLM。

建议市场试用前至少运行：

```bash
cd /path/to/ManJuFlow
python -m pytest tests/api
```

## 8. 前端验收清单

浏览器检查项：

- Sidebar 是否有“已有剧本”入口；
- 粘贴文本是否能切分；
- mock 上传是否填充 `extracted_text`；
- 切分结果是否展示；
- 复制 / 导出是否成功；
- 是否能带入分镜；
- 是否能从分镜带入 Prompt；
- loading / error / empty state 是否清楚；
- 页面是否没有明显英文混杂，除技术字段外；
- 不需要重启时是否能热更新。

建议完整浏览器链路：

```text
已有剧本
  -> 粘贴虚构文本
  -> 切分
  -> 查看 segments
  -> 带入分镜
  -> 生成分镜
  -> 带入绘图 Prompt
  -> 生成 Prompt
  -> 复制 / 导出
```

## 9. 当前差距与后续小闭环

根据目前已知状态，后续还需要继续验证或补齐：

- 是否已经支持切分结果一键带入 ImagePrompt，还是需要先生成 Storyboard 再带入 Prompt；
- 是否需要增加“从切分结果直接进入 Prompt 链路”的前端按钮；
- 是否需要优化 `ScriptSegmentationWorkspace` 文案；
- 是否需要真实 multipart `.docx` 上传；
- 是否需要保存上传 metadata；
- 是否需要 `workspace_id` / `project_id` / `session_id` 透传；
- 是否需要 Assistant suggested action 触发切分 / 分镜 / Prompt；
- 是否需要保存切分版本，支持回退或比较；
- 是否需要区分“切分用于分镜”和“切分用于改写”的不同目标。

这些差距不阻塞老板演示，但会影响市场试用版的稳定性、可追踪性和协作体验。

## 10. 风险与边界

必须明确：

- 不用真实客户剧本做公开演示；
- mock upload 不能说成真实上传；
- 10 万字符限制不是单次 LLM 调用上限；
- 长剧本后续需要 chunking；
- 上传文件不进入 Git；
- 公开仓库不保存真实剧本；
- 市场试用前要加隐私提示；
- 结果应允许人工确认和编辑；
- AI 输出不应被直接视为最终定稿。

## 11. 第 170 步验收标准

- `docs/EXISTING_SCRIPT_WORKFLOW_ACCEPTANCE.md` 已新增；
- 文档明确核心链路；
- 文档明确老板演示验收标准；
- 文档明确市场试用验收标准；
- 文档包含安全虚构测试数据；
- 文档包含前端验收清单；
- 文档不夸大 mock 上传；
- 文档不包含敏感信息；
- 不修改代码。
