# Auth Persistence SQLite Design｜内部账号持久化 SQLite 设计

## 1. 背景与目标

当前 Internal Auth 第一层已经完成：

- Auth schema；
- password policy helper；
- 密码规则：至少 8 位，包含大写字母、小写字母和数字；
- in-memory internal auth service；
- `POST /api/auth/login`；
- `GET /api/auth/safe-users`；
- 前端登录按钮已调用后端 auth API；
- 登录后 `authContext` 进入 React state；
- `context_options` 已优先使用 auth response 中的 user / session / workspace / context_policy；
- 当前账号 `safe_creator` / `SafePass123` 只用于开发期安全虚构测试，不是真实员工账号。

第 341 步目标是设计 SQLite 最小持久化方案，为第 342～346 步落地做准备。本步不写代码、不创建数据库文件、不接真实员工账号。

本方案只服务 Dramora 短中期公司内部 5～10 人稳定使用，不做生产级复杂权限系统，不引入 Redis / OAuth / SSO / 多租户。

## 2. 当前不解决的问题

本阶段暂不做：

- 生产级 SSO；
- OAuth；
- 手机号实名注册；
- 多租户复杂权限；
- Redis session；
- 复杂 RBAC；
- 管理后台完整用户管理；
- 邮件找回密码；
- 第三方登录；
- 对外 SaaS 注册；
- 真实员工数据提交到公开仓库。

这些能力如果后续需要，应在内部试用稳定后单独设计，不作为 SQLite 最小落地的前置条件。

## 3. SQLite 最小落地边界

SQLite 只作为内部试运行阶段的最小持久化方案：

- 适合 5～10 人内部稳定试用；
- 单机部署简单；
- 易备份；
- 易迁移到 PostgreSQL；
- 比 in-memory auth 更接近真实使用；
- 数据库文件必须进入 `.gitignore`；
- 数据库文件不能提交公开仓库。

SQLite 的目标是让账号、密码哈希、账号状态和最近登录时间可持续保存，而不是一次性实现完整企业级 IAM。

## 4. 建议用户表 users 设计

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| `id` | text / uuid-like string | 内部用户主键，后续映射 `user_id`。 |
| `username` | text unique not null | 登录用户名，支持中文和英文。 |
| `display_name` | text nullable | 展示名。 |
| `password_hash` | text not null | 只保存 hash，不保存明文密码。 |
| `role` | text not null | 第一版可为 `admin` / `creator` / `reviewer`。 |
| `workspace_id` | text not null | 第一版可默认 `workspace_dramora_internal`。 |
| `default_project_id` | text nullable | 默认项目，可后续接项目表。 |
| `is_active` | integer / boolean | 用于禁用账号。 |
| `created_at` | text datetime | 创建时间。 |
| `updated_at` | text datetime | 更新时间。 |
| `last_login_at` | text datetime nullable | 最近登录时间。 |
| `password_updated_at` | text datetime nullable | 最近密码更新时间。 |

设计说明：

- `username` 支持中文和英文用户名；
- `password_hash` 只保存 hash，不保存明文；
- `role` 第一版不需要复杂 RBAC，可先覆盖 admin / creator / reviewer；
- `workspace_id` 第一版可默认 internal；
- `is_active` 用于禁用账号；
- 不保存真实密码；
- 不保存 API Key；
- 不保存员工隐私扩展字段。

## 5. 密码与 password_hash 策略

密码策略继续沿用当前 password policy：

- 至少 8 位；
- 包含大写字母；
- 包含小写字母；
- 包含数字；
- 后续可增强特殊字符和最小长度。

后端只保存 `password_hash`，不保存明文密码。推荐使用 `passlib` / `bcrypt` 或同等成熟方案，但本步不引入依赖，只做设计。

测试 seed user 只能使用安全虚构账号。公开仓库禁止提交真实 `password_hash`，也禁止提交来自真实密码生成的 hash。

## 6. 安全虚构 seed user 策略

可以保留 `safe_creator` 作为开发期 seed user：

- `safe_creator` 是安全虚构账号；
- `SafePass123` 只用于开发和测试；
- 未来部署前必须替换；
- seed 数据可以通过脚本生成；
- seed 脚本不得包含真实账号；
- 文档中不要写真实员工账号；
- README 和公开示例只能使用安全虚构账号。

部署前应有明确步骤：创建真实内部账号、禁用或删除开发期 seed user、确认数据库文件和 seed 输出不进入公开仓库。

## 7. Auth repository 设计

后续可新增：

```text
apps/api/app/repositories/auth_repository.py
```

如果项目后续形成统一 persistence 层，也可以调整路径，但 repository 职责应保持清晰。

建议 repository 方法：

- `get_user_by_username(username)`；
- `create_user(...)`；
- `update_last_login(user_id)`；
- `list_safe_users()`；
- `deactivate_user(user_id)`；
- `verify_user_exists(username)`。

职责边界：

- repository 负责 SQLite 读写；
- service 负责业务规则、password policy、password hash verify、登录失败统一错误；
- router 只负责请求 / 响应和 HTTP 状态码转换；
- 前端不感知底层存储是 in-memory 还是 SQLite。

## 8. Auth service 迁移策略

第 344 步建议将当前 `auth_service.py` 从 in-memory 数据源切到 repository：

- 保留 service 对外函数签名尽量稳定；
- `authenticate_internal_user(username, password)` 继续返回 `AuthLoginOutput`；
- `get_safe_internal_user(username)` / `list_safe_internal_users()` 尽量保持兼容；
- endpoints 尽量不感知底层存储变化；
- 前端 `authContext` 不应因为后端存储变化而大改；
- 登录失败统一友好提示；
- 错误响应不能泄露用户名是否存在的敏感细节过多。

迁移时应先写 repository 测试，再切 service，最后跑 endpoint 和前端 e2e 回归。

## 9. Token / Session 第一版策略

当前已经有 `session_id` / `context_options`，但尚未完成正式 token 签名、过期、刷新和撤销。

第一版建议：

- 登录响应继续返回 user / session / workspace / context_policy；
- SQLite 持久化优先解决用户表和 `password_hash`；
- session_id 可继续作为业务上下文 ID；
- signed token / 过期 / 刷新后续单独小步接入；
- 不在第 342～346 步中一次性做完整 JWT 系统，除非后续明确安排。

这样可以降低风险，避免把用户表、密码哈希、JWT、刷新 token、权限中间件一次性混在一个大步骤里。

## 10. 与 ContextOptions 的关系

`user_id` / `workspace_id` / `project_id` / `session_id` / `context_policy` 是业务上下文边界。同一个 LLM API Key 不是用户隔离边界。

登录成功后的 auth response 继续驱动 `context_options`：

- 生成；
- 文档导入；
- 文档导出；
- Usage Ledger；
- 后续质量评审。

`context_policy` 默认 `current_project_only`。任何跨项目、跨 workspace 的历史读取都必须单独设计授权和 UI 提示，不能隐式拼接到 LLM prompt。

## 11. 与 Usage Ledger 的关系

Auth 持久化完成后，Usage Ledger 应记录：

- `user_id`；
- `workspace_id`；
- `project_id`；
- `session_id`；
- `operation`；
- `provider`；
- `model`；
- `purpose`；
- `status`；
- `request_id`；
- `estimated_cost_cny`。

Usage Ledger 不记录：

- 完整剧本文本；
- 完整上传文件；
- provider 原始响应；
- API Key；
- 密码；
- token；
- 本机绝对路径。

后续第 347～351 步再做 Usage Ledger 持久化，不要和 Auth SQLite 最小落地混成一个大改动。

## 12. 错误响应与日志脱敏

错误响应与日志必须遵守：

- 登录失败不返回 `password_hash`；
- 登录失败不返回内部堆栈；
- 登录失败不返回数据库路径；
- 登录失败不返回真实服务器路径；
- 日志中不打印密码；
- 日志中不打印 token；
- 公开仓库不提交本地数据库；
- 测试日志不包含真实账号；
- `safe-users` 不返回 `password_hash`；
- 登录失败提示不区分账号不存在还是密码错误。

推荐继续使用统一错误文案，例如“账号或密码不正确。”。

## 13. 后续步骤映射

建议后续小步：

- 第 342 步：Auth repository schema / SQLite 用户表设计；
- 第 343 步：`password_hash` 接入与安全虚构 seed user；
- 第 344 步：auth service 从 in-memory 切到 repository；
- 第 345 步：auth endpoints 回归 + 错误提示安全检查；
- 第 346 步：前端登录 e2e 回归 + 文档同步。

每一步都应避免真实员工账号、真实密码、真实 token、真实数据库文件进入仓库。

## 14. Go / No-Go 标准

完成 Auth 持久化后至少要满足：

- 后端 auth schema 测试通过；
- repository 测试通过；
- service 测试通过；
- endpoint 测试通过；
- 登录失败不会泄露敏感信息；
- `safe-users` 不返回 `password_hash`；
- 前端登录流程可用；
- `context_options` 正确沿用登录返回；
- 数据库文件不进入 git；
- git status clean；
- README / Roadmap / Runbook 同步。

No-Go 条件：

- 需要提交真实数据库文件；
- 需要提交真实员工账号或密码；
- 需要提交真实 `password_hash`；
- 登录失败暴露账号是否存在；
- `safe-users` 暴露密码或 hash；
- token secret 需要进入公开仓库；
- 测试依赖真实服务器或真实员工数据。
