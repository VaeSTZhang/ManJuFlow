# ComfyUI Private Integration Checklist｜私有小样本联调检查表

## 1. 文档定位

本文档用于未来判断是否进入真实 ComfyUI / 远端 GPU 小样本联调。

当前阶段不需要购买服务器，不需要安装 ComfyUI，也不需要准备真实 workflow。当前阶段继续使用 mock provider。只有所有前置条件满足后，才考虑真实联调。

本文档不包含真实服务器地址、API Key、SSH Key、真实 workflow、真实 workflow 文件名、模型权重路径或客户数据。

## 2. 当前结论

当前不需要购买远端 GPU。

当前不需要安装 ComfyUI。

当前不需要准备模型权重。

当前不需要准备真实 workflow。

当前不需要配置真实对象存储。

当前不需要进行批量生产。

## 3. 进入真实联调前必须完成的公开仓库条件

进入真实联调前，公开仓库应满足：

- [ ] ImageGeneration Schema 稳定；
- [ ] mock service 稳定；
- [ ] `/api/images/generate` mock endpoint 稳定；
- [ ] 前端 Image Generation mock UI 稳定；
- [ ] provider interface 稳定；
- [ ] ComfyUI placeholder 存在；
- [ ] workflow registry 设计已完成；
- [ ] ComfyUI provider 技术方案已完成；
- [ ] 私有部署 runbook 已完成；
- [ ] `.env.example` 只有安全占位；
- [ ] README 已说明 public repo safety boundary；
- [ ] `tests/api` 通过；
- [ ] `npm run build` 通过；
- [ ] `git status` clean；
- [ ] `origin/main` 已同步或本地 commit 安全。

## 4. 进入真实联调前必须完成的私有环境准备

进入真实联调前，私有环境应满足：

- [ ] 已选择按量 GPU 或可控成本环境；
- [ ] 已明确预算上限；
- [ ] 已明确只跑 1-2 条 `prompt_items`；
- [ ] 已准备私有 `.env`；
- [ ] 已准备私有 workflow registry；
- [ ] 已准备真实 ComfyUI workflow；
- [ ] 已准备模型权重；
- [ ] 已准备访问认证；
- [ ] 已确认不会公网裸奔；
- [ ] 已确认日志脱敏；
- [ ] 已确认输出资产存储位置；
- [ ] 已确认失败时如何停止任务；
- [ ] 已确认不会把私有配置提交 Git。

## 5. 最小联调样本建议

未来小样本只建议使用：

- 1 个 `project_title`；
- 1-2 个 `prompt_items`；
- `output_count = 1`；
- `provider = comfyui`；
- 虚构测试内容；
- 不使用客户素材；
- 不使用合作方资料。

示例主题可使用虚构内容，例如“雨夜医院门口重逢”。不要使用客户剧本、客户角色、合作方资料或任何真实生产素材。

## 6. 联调成功标准

真实小样本联调成功标准：

- `/api/images/generate` 返回 200；
- 返回 `ImageGenerationOutput`；
- 每个 item 有 `task_id` / `prompt_id` / `shot_id`；
- 有 `image_url` 或 `local_path`；
- `status` 为 `succeeded`；
- `metadata` 不泄露敏感信息；
- 前端能展示结果；
- 日志不泄露密钥、workflow 路径、服务器地址；
- 成本可控。

## 7. 联调失败停止条件

出现以下任一情况，应立即停止真实联调，回退到 mock provider：

- API Key 或 token 出现在日志；
- workflow 路径出现在公开输出；
- 服务器地址被写入代码或文档；
- 任务无限重试；
- 成本不可控；
- 输出资产路径混乱；
- 生成失败无法定位；
- 本地 mock 行为被破坏；
- `git status` 出现不应提交的敏感文件。

停止后应先清理敏感信息、恢复 mock 行为、补充 checklist，再决定是否重新联调。

## 8. 成本控制

成本控制规则：

- 初次只用按量；
- 不包月；
- 不做批量；
- 不开并发；
- 不开无限重试；
- 每次联调记录时长和费用；
- 先验证一张图，再考虑多图。

在成本记录和失败处理机制稳定前，不进入批量任务。

## 9. 安全检查

安全检查项：

- [ ] `.env` 不提交；
- [ ] workflow 不提交；
- [ ] 模型权重不提交；
- [ ] 输出图片不提交；
- [ ] 客户素材不提交；
- [ ] token 不出现在日志；
- [ ] `server_url` 不写入 README；
- [ ] 私有 registry 不进入公开仓库；
- [ ] 终端截图发布前检查敏感信息。

## 10. 决策规则

只有当公开仓库条件、私有环境准备、安全检查、成本控制全部满足后，才可以进入真实 ComfyUI 小样本联调。

如果任一条件不满足，继续停留在 mock provider 阶段。

## 11. 后续步骤建议

建议后续步骤：

- 第 118 步：更新 `PHASE_4_PROGRESS` / `README` 文档索引，加入 checklist 和 provider design；
- 第 119 步：评估是否进入远端 GPU 准备；
- 如果暂不进入真实服务器，则继续做 asset manager / task status mock；
- 真正需要服务器时，再单独输出采购 / 租用建议。

在用户明确需要真实服务器前，不提前购买或租用远端 GPU。
