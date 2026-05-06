# Local Internal Trial Safety Runbook｜本地 / 单机内部试运行安全手册

## 1. 适用范围

本文档用于 Dramora 在服务器购买和云端部署前的本地 / 单机内部试运行阶段。

它不是云端生产部署文档，不是公网开放方案，也不涉及域名、HTTPS、Nginx、备案或正式多租户运维。当前目标是服务公司内部 5～10 人小范围稳定试用前的安全准备，确保项目结构、数据目录、环境变量、数据库文件、日志、导入文件和导出文件不会混乱或误提交。

本 Runbook 只覆盖本地开发机或单机内部试运行的安全边界。进入公网服务器、域名、HTTPS 和内部长期运行前，应另开部署上线阶段文档。

## 2. 当前能力状态

当前 Dramora 已具备以下本地落地基础：

- 三入口剧本生成与改编：`idea` / `film_script` / `novel`；
- 统一 `ShortDramaScriptOutput` 结构；
- 生成结果在线审看与基础字段编辑；
- Word `.docx` 导入预览；
- TXT / JSON / DOCX 导出；
- Internal Auth SQLite repository + `password_hash`；
- Usage Ledger SQLite repository；
- Project / Session / Document ownership repository；
- `ContextOptions` 已覆盖生成、导入、导出；
- 前端 e2e 已覆盖登录、三入口、导入、编辑、导出；
- 后端全量测试已通过；
- 旧兼容测试误触发真实 LLM 的慢测试问题已修复，`pytest` 可离线快速运行。

这些能力说明本地内部试运行的基础链路已接近完整，但不代表已经完成生产级权限、部署或运维能力。

## 3. 当前明确不是生产级能力

当前仍未完成：

- 真实内部员工账号替换；
- 正式 token 生命周期、过期和刷新；
- 权限中间件；
- 管理员后台；
- 云端部署；
- Nginx / HTTPS；
- 服务器防火墙；
- 数据库加密；
- 自动备份；
- 日志轮转；
- 真实生产审计后台；
- Usage Ledger 查询 UI；
- 完整项目管理后台；
- 多人协同编辑。

因此当前只能作为本地 / 单机内部试运行准备，不应对外宣称已经生产上线或具备正式多人权限系统。

## 4. 本地试运行目录边界

本地运行数据目录与备份策略见 [Local Data Storage and Backup Plan｜本地数据目录与备份方案](LOCAL_DATA_STORAGE_AND_BACKUP_PLAN.md)。第 359 步已完成数据库文件、上传目录、导出目录、日志目录保护方案。

以下目录或文件可以在本地运行时出现，但不能提交到公开仓库：

- `.local/`
- `apps/api/.local/`
- `uploads/`
- `exports/`
- `generated/`
- `outputs/`
- `dist/`
- `apps/web/dist/`
- `playwright-report/`
- `test-results/`
- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `*.log`

目录边界要求：

- SQLite 数据库文件只应放在 `.local/` 或 `apps/api/.local/`；
- 上传文件和导出文件不进入 git；
- 真实客户文档不放入公开仓库目录；
- 临时测试文件用完即删，或放到明确被 `.gitignore` 覆盖的目录；
- 构建产物、测试报告、浏览器录制结果和缓存都不提交。

## 5. 环境变量安全边界

真实配置只放项目根目录 `.env`。`.env` 不提交，`.env.example` 只放占位变量。

环境变量完整清单见 [Environment Variables｜环境变量清单](ENVIRONMENT_VARIABLES.md)。第 358 步已完成 `.env.example` / 环境变量清单 / 敏感信息检查收口。

环境变量规则：

- 不再维护 `apps/api/.env`；
- 不在 README / docs / tests 中写真实 key；
- 不在终端反馈里粘贴 `.env` 内容；
- 不把 API Key 截图或复制到公开聊天、公开 issue 或公开 PR；
- 私有部署环境的 secret 只通过私密运维渠道传递。

重点检查变量类别：

- `DEFAULT_LLM_PROVIDER`
- `DEEPSEEK_API_KEY`
- `MIMO_API_KEY`
- `KIMI_API_KEY`
- `MINIMAX_API_KEY`
- `SCRIPT_GENERATION_MODE`
- `DRAMORA_AUTH_DB_PATH`
- `DRAMORA_USAGE_LEDGER_DB_PATH`
- `DRAMORA_OWNERSHIP_DB_PATH`
- 未来 token secret / session secret

本地试运行中，如果 `SCRIPT_GENERATION_MODE=llm`，自动化测试仍必须通过测试内 monkeypatch 或 route mock 保持离线稳定，不允许误触发真实 provider。

## 6. SQLite 数据库文件策略

当前本地可能出现以下 SQLite 数据库：

- `.local/dramora_usage_ledger.sqlite3`
- `.local/dramora_ownership.sqlite3`
- `apps/api/.local/dramora_auth.sqlite3`

数据库文件策略：

- 数据库文件不提交；
- `git ls-files` 不应出现 `.db` / `.sqlite` / `.sqlite3`；
- 试运行前先备份；
- 试运行后定期备份；
- 不把数据库发到公开 GitHub；
- 不把数据库直接发给外部合作方；
- 如需迁移服务器，应通过私密通道和单独部署文档处理；
- 数据库文件如包含真实内部账号或使用记录，应视为敏感文件。

## 7. 上传 / 导出文件策略

Word 上传只用于导入原文和生成导入预览。上传后用户必须明确选择填入、追加或取消，系统不应自动决定改编方向。

上传与导出规则：

- 当前系统不应把完整上传文件提交 git；
- 导出 DOCX / TXT / JSON 只作为用户下载结果；
- 导出文件不进入公开仓库；
- 测试文件必须是安全虚构内容；
- 真实客户剧本必须保存在私有环境；
- 真实客户 Word 文件不放入公开仓库目录；
- 导入预览、Usage Ledger 和 ownership 记录只保存脱敏摘要，不保存完整 Word bytes 或完整正文。

## 8. 日志与错误响应边界

第 360 步已完成日志脱敏、错误响应和安全边界检查。安全测试覆盖 Auth、Script Generation、Document Import、Document Export 和 Ownership guardrails；当前仍未进入云端部署。

日志和错误响应不得包含：

- API Key；
- password；
- `password_hash`；
- token；
- provider 原始响应；
- 完整 `source_text`；
- 完整 `extracted_text`；
- 完整 DOCX bytes；
- 本机绝对路径；
- 真实客户剧本。

当前 Usage Ledger 只记录脱敏摘要，例如 operation、provider、model、source mode、字符数、文件大小、状态、安全错误码和 project/session 归属。Usage Ledger 不记录完整剧本文本、完整上传文件、完整模型原始响应或密钥。

## 9. 本地试运行前检查清单

每次开始本地 / 单机内部试运行前，至少执行：

```bash
git status

git diff --stat

git ls-files | grep -E '\.(db|sqlite|sqlite3)$|^\.local/' || true

find . -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3"

grep -R "DEEPSEEK_API_KEY\|MIMO_API_KEY\|KIMI_API_KEY\|MINIMAX_API_KEY\|password_hash\|access_token\|/Users/" README.md README.zh-CN.md README.en.md docs apps/api/app apps/web/src tests/api | head -120

python -m pytest tests/api

cd apps/web
npm run build
npm run test:e2e
```

注意：

- grep 命中安全文档说明或测试 forbidden key 清单时要看上下文；
- 真正不能出现的是实际 key、真实路径、真实密码、真实客户内容；
- 如果本地 `python` 不在 PATH，可使用项目虚拟环境中的 Python；
- 如果 Playwright 需要启动本地 dev server，应确保端口未被占用。

## 10. 本地试运行启动流程

以下命令使用通用占位路径，避免在公开文档中写入真实用户名路径。

后端启动：

```bash
cd /path/to/Dramora
source .venv/bin/activate
bash scripts/dev_api.sh
```

端口占用清理并重启：

```bash
cd /path/to/Dramora
source .venv/bin/activate
bash scripts/kill_api_port.sh
bash scripts/dev_api.sh
```

前端启动：

```bash
cd /path/to/Dramora/apps/web
npm run dev
```

说明：

- 本地试运行不要使用公开服务器地址；
- 不在文档中写真实服务器 IP 或域名；
- `scripts/dev_api.sh` 会在本地启动 FastAPI；
- `scripts/kill_api_port.sh` 只用于清理本地 API 端口占用；
- 前端 dev server 仅用于本地内部测试。

## 11. 本地试运行功能验收流程

本地试运行至少覆盖：

- 登录；
- 选择三入口；
- `idea` 生成；
- `film_script` 改编；
- `novel` 改编；
- Word 导入预览；
- 导入预览后的填入 / 追加 / 取消；
- 在线编辑；
- TXT 导出；
- JSON 导出；
- DOCX 导出；
- Usage Ledger 是否写入；
- Project / Session / Document ownership 是否写入；
- 错误输入是否给出友好提示；
- UI 不出现 mock / 后端 mock / 本地演示等开发文案；
- 页面不显示 password、`password_hash`、token 或 API Key。

验收时只使用安全虚构样本。真实客户内容只应在私有环境中处理，并遵守内部资料管理要求。

## 12. 备份与回滚策略

备份策略：

- 备份 `.local/` 下的 SQLite 数据库；
- 备份私有 `.env`；
- 不把备份放进 git；
- 数据库迁移前先复制备份；
- 内部试运行中形成的真实数据只能通过私密通道保存和迁移。

回滚策略：

- 更新前先确保 `git status clean`；
- 未提交改动出错时可使用 `git restore` 谨慎恢复；
- 已提交但未推送的改动需先确认影响，再考虑 reset；
- 已推送改动不要随意 force push；
- 数据库文件和代码回滚分开处理，不能用 git 回滚替代数据库备份。

## 13. GitHub 公开仓库安全检查

服务器购买前必须梳理 GitHub 与本地项目文件结构，避免：

- `App.tsx` 继续膨胀；
- `CreationHome` 继续膨胀；
- services 无序堆积；
- routers 无序堆积；
- docs 失控；
- 历史 ManJuFlow / Prompt / Assistant 表述干扰 Dramora 当前定位；
- `dist` / reports / db / upload 文件误提交；
- README 过期；
- `.env.example` 被误写真实值；
- 测试 fixture 混入真实客户剧本或真实上传文件。

公开仓库只应保留代码、测试、文档和安全虚构样例。

## 14. 服务器购买前必须完成的事项

服务器购买前建议继续完成：

- 第 358 步：`.env.example` / 环境变量清单 / 敏感信息检查；
- 第 359 步：数据库文件、上传目录、导出目录、日志目录保护方案；
- 第 360 步：日志脱敏、错误响应、安全边界检查；
- 第 361 步：后端全量 `pytest`；
- 第 362 步：前端 build + e2e；
- 第 363 步：真实 DeepSeek 三入口小样本复测；
- 第 364 步：Word 导入 → 生成 → 编辑 → DOCX 导出全链路验收；
- 第 365 步：内部账号登录 → 生成 → 用量记录归属验收；
- 第 366 步：README / Roadmap / Runbook / Go-No-Go checklist 最终同步。

这些步骤完成前，不建议把本地临时状态直接搬上云。

## 15. 什么时候可以新开服务器部署对话

当第 366 步完成，并且 Go / No-Go checklist 通过后，可以新开：

```text
06｜部署上线｜服务器、域名、数据库、HTTPS 与内部试运行
```

在此之前不要急着买服务器，不要把本地开发期临时状态直接搬上云，不要把 `.env`、SQLite 数据库、上传文件或导出文件提交到公开仓库。
