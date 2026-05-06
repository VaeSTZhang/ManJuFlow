# Local Data Storage and Backup Plan｜本地数据目录与备份方案

## 1. 适用范围

本文档用于 Dramora 本地 / 单机内部试运行阶段，聚焦以下运行数据的目录边界、备份策略和迁移前检查：

- SQLite 数据库文件；
- 上传文件；
- 导出文件；
- 日志文件；
- 测试报告；
- 构建产物；
- 临时输出目录；
- 服务器部署前迁移准备。

本文档不是云端对象存储方案，不是生产备份系统，不包含真实服务器路径，不包含真实客户内容，也不包含真实账号或密钥。

## 2. 本地运行数据分类

### A. SQLite 数据库

当前可能出现：

- `.local/dramora_usage_ledger.sqlite3`
- `.local/dramora_ownership.sqlite3`
- `apps/api/.local/dramora_auth.sqlite3`

这些文件可能包含内部账号、用量记录、项目 / 会话 / 文档归属等运行数据，必须视为敏感文件。

### B. 上传文件

可能出现：

- `uploads/`
- `apps/api/uploads/`
- `apps/api/app/storage/`
- 后续真实 Word 上传目录

Word 上传可能包含真实剧本、版权文本或客户资料。当前阶段不应把完整上传文件纳入公开仓库。

### C. 导出文件

可能出现：

- `exports/`
- `apps/api/exports/`
- 用户下载的 TXT / JSON / DOCX

导出文件可能包含完整剧本文本，不应进入 git 或公开仓库。

### D. 生成与输出目录

可能出现：

- `generated/`
- `outputs/`

这些目录用于本地临时生成结果、调试输出或后续批处理结果，不能存放需要提交的源码。

### E. 前端构建与测试产物

可能出现：

- `apps/web/dist/`
- `playwright-report/`
- `test-results/`

这些产物可重新生成，不应提交。

### F. 日志文件

可能出现：

- `*.log`
- `logs/`
- `apps/api/logs/`

日志可能包含错误摘要、请求路径和运行上下文，必须脱敏并保持在 git ignore 范围内。

## 3. `.gitignore` 保护要求

`.gitignore` 必须覆盖：

- `.env`
- `.env.*`
- `!.env.example`
- `.local/`
- `apps/api/.local/`
- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `uploads/`
- `apps/api/uploads/`
- `exports/`
- `apps/api/exports/`
- `generated/`
- `outputs/`
- `apps/web/dist/`
- `playwright-report/`
- `test-results/`
- `backups/`
- `logs/`
- `apps/api/logs/`
- `*.log`

要求：

- 检查 `.gitignore` 是否包含这些规则；
- 如缺失，只做小范围追加；
- 不删除已有规则；
- 不把 `.env.example` 忽略掉。

## 4. SQLite 数据库保护策略

SQLite 数据库文件不进入 Git。

数据库可能包含：

- 内部账号；
- `password_hash`；
- Usage Ledger；
- project / session / document 归属；
- 请求归属、模型 provider、模型名称、用量摘要；
- 脱敏错误码与状态。

保护策略：

- 数据库文件属于敏感运行数据；
- 本地试运行前先备份；
- 内部试运行后定期备份；
- 重要功能升级前备份；
- 迁移服务器前单独导出或复制；
- 不通过公开 GitHub、公开聊天、公开网盘传递数据库；
- 不把数据库作为测试 fixture 提交。

建议备份命名：

```text
backups/YYYY-MM-DD/dramora_auth.sqlite3
backups/YYYY-MM-DD/dramora_usage_ledger.sqlite3
backups/YYYY-MM-DD/dramora_ownership.sqlite3
```

`backups/` 必须被 `.gitignore` 覆盖。

## 5. 上传文件保护策略

Word 上传可能包含真实剧本、版权文本或客户资料。

上传文件策略：

- 上传文件不进入 Git；
- 测试只能使用安全虚构文件；
- 真实客户文件应放私有环境；
- 上传目录后续服务器部署时应单独规划权限和备份；
- 当前系统只记录导入预览和安全摘要；
- 当前不应长期保存完整上传文件，除非后续明确设计 Asset / File Manager；
- 不把真实 Word 上传文件作为公开测试 fixture。

## 6. 导出文件保护策略

TXT / JSON / DOCX 导出是用户结果文件，可能包含完整剧本文本。

导出文件策略：

- 不进入 Git；
- 不进入公开仓库；
- 不作为测试 fixture 提交，除非内容安全虚构且体积可控；
- 后续服务器部署时应考虑下载有效期；
- 后续服务器部署时应考虑文件清理；
- 后续服务器部署时应考虑权限校验；
- 如需保存导出历史，应单独设计文件资产策略。

## 7. 日志保护策略

日志不得包含：

- API Key；
- password；
- `password_hash`；
- token；
- provider 原始响应；
- 完整剧本文本；
- 完整上传文件内容；
- DOCX bytes；
- 本机绝对路径；
- 真实服务器地址。

本地日志可以辅助排查，但不提交 Git。第 360 步会专门做日志脱敏、错误响应和安全边界检查。

## 8. 备份策略

本地 / 单机内部试运行建议：

- 每次内部试运行前备份 SQLite；
- 每次重要功能升级前备份 SQLite；
- 每天或每轮测试后备份；
- 备份文件不进 Git；
- 备份文件不发公开渠道；
- 备份文件应和 `.env` 分开管理；
- 数据库备份和代码版本号 / commit hash 建议一起记录。

建议备份记录包含：

- commit hash；
- backup date；
- database files；
- notes；
- operator。

备份记录本身如果包含真实员工姓名、客户项目名或内部备注，也不能提交公开仓库。

## 9. 清理策略

可定期清理：

- 临时上传文件；
- 临时导出文件；
- `playwright-report/`；
- `test-results/`；
- `apps/web/dist/`；
- `__pycache__/`；
- `*.pyc`；
- 临时输出目录。

清理注意：

- `apps/web/dist/` 可重新生成；
- `playwright-report/` / `test-results/` 可随时删除；
- `.local` SQLite 不要随意删除；
- 删除 SQLite 前必须备份；
- 真实客户文件删除需遵守公司内部资料规则；
- 清理动作不要混入业务代码提交。

## 10. 服务器迁移前数据检查

迁移服务器前必须确认：

- `git status clean`；
- 公开仓库无数据库文件；
- 公开仓库无上传文件；
- 公开仓库无导出文件；
- 公开仓库无真实客户剧本；
- 公开仓库无真实 `.env`；
- 数据库备份已完成；
- 服务器目录结构另行设计；
- 生产 secret 另行配置；
- 不直接把整个本地目录 rsync 到服务器。

服务器目录、对象存储、日志目录、备份目录、权限模型和 HTTPS / CORS 必须在部署阶段单独设计。

## 11. 本地检查命令

提交前或内部试运行前建议执行：

```bash
git status

git diff --stat

git ls-files | grep -E '\.(db|sqlite|sqlite3)$|^\.local/' || true

git ls-files | grep -E 'uploads/|exports/|generated/|outputs/|playwright-report|test-results|apps/web/dist|logs/' || true

find . -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3"

find . -path "*/playwright-report/*" -o -path "*/test-results/*" -o -path "*/dist/*"

grep -R "API Key\|password_hash\|access_token\|provider_raw_response\|/Users/" README.md README.zh-CN.md README.en.md docs apps/api/app apps/web/src tests/api | head -120
```

说明：

- grep 命中文档说明或 forbidden key 清单时要看上下文；
- 不允许出现真实 key、真实 hash、真实 token、真实本机路径或真实客户内容；
- 本地 SQLite 文件可以存在，但必须未被 git 跟踪；
- 构建产物和测试报告可以存在，但必须未被 git 跟踪。

## 12. 与第 360～366 步的关系

- 第 360 步会做日志脱敏、错误响应、安全边界检查；
- 第 361～362 步做后端 / 前端总回归；
- 第 363～365 步做真实模型与全链路验收；
- 第 366 步做 README / Roadmap / Runbook / Go-No-Go checklist 最终同步；
- 第 366 步前不建议购买服务器；
- 第 366 步后可以新开部署上线对话。
