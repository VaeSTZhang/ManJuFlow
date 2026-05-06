# Environment Variables｜环境变量清单

## 1. 适用范围

本文档记录 Dramora 本地开发、本地 / 单机内部试运行和后续部署准备阶段需要关注的环境变量。

当前文档不是云端生产部署文档，不包含真实 API Key、真实服务器地址、真实员工账号、真实密码、真实 token secret 或真实数据库文件路径。

## 2. `.env` 与 `.env.example` 规则

- `.env` 只保存在本地或私有部署环境；
- `.env` 不提交公开仓库；
- `.env.example` 只放占位值；
- 不再维护 `apps/api/.env`；
- README、docs、tests 中不得写真实 key；
- 不要把 `.env` 内容贴到公开聊天、issue、PR 或截图；
- 私有部署环境的 secret 应通过私密运维渠道配置。

## 3. 基础运行变量

| 变量 | 示例占位值 | 说明 |
| --- | --- | --- |
| `APP_NAME` | `Dramora` | 应用名称。 |
| `APP_ENV` | `development` | 本地 / 内部试运行环境标记。 |
| `SCRIPT_GENERATION_MODE` | `mock` | 剧本生成模式，支持 `mock` / `llm`。 |
| `STORYBOARD_GENERATION_MODE` | `mock` | 分镜生成模式。 |
| `IMAGE_PROMPT_GENERATION_MODE` | `mock` | 图片 Prompt 生成模式。 |
| `ASSISTANT_GENERATION_MODE` | `mock` | 历史 Assistant 相关占位，当前不恢复右侧聊天式 Assistant。 |

自动化测试必须保持离线稳定。即使本地 `.env` 设置为 `SCRIPT_GENERATION_MODE=llm`，测试也应通过 monkeypatch 或 route mock 避免真实 provider 调用。

## 4. LLM Provider 变量

| 变量 | 示例占位值 | 说明 |
| --- | --- | --- |
| `DEFAULT_LLM_PROVIDER` | `deepseek` | 默认 provider。 |
| `DEFAULT_SCRIPT_MODEL` | `deepseek-chat` | 默认剧本模型。 |
| `LLM_REQUEST_TIMEOUT_SECONDS` | `60` | LLM 请求超时。 |
| `LLM_PROVIDER` | 空 | 兼容字段。 |
| `LLM_BASE_URL` | 空 | OpenAI-compatible fallback endpoint，占位即可。 |
| `LLM_MODEL` | 空 | OpenAI-compatible fallback model，占位即可。 |
| `LLM_API_KEY` | `your_key_here` | fallback key 占位，不填真实值。 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | DeepSeek provider endpoint。 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | DeepSeek 默认模型。 |
| `DEEPSEEK_API_KEY` | `your_deepseek_api_key_here` | 占位值，不填真实 key。 |
| `MIMO_BASE_URL` | `https://api.xiaomimimo.com` | Mimo provider endpoint。 |
| `MIMO_MODEL` | `mimo-v2.5-pro` | Mimo 默认模型。 |
| `MIMO_API_KEY` | `your_mimo_api_key_here` | 占位值，不填真实 key。 |
| `KIMI_BASE_URL` | `https://api.moonshot.cn` | Kimi provider endpoint。 |
| `KIMI_MODEL` | `kimi-k2.5` | Kimi 默认模型。 |
| `KIMI_API_KEY` | `your_kimi_api_key_here` | 占位值，不填真实 key。 |
| `MINIMAX_BASE_URL` | `https://api.minimaxi.com` | MiniMax provider endpoint。 |
| `MINIMAX_MODEL` | `MiniMax-M2.7` | MiniMax 默认模型。 |
| `MINIMAX_API_KEY` | `your_minimax_api_key_here` | 占位值，不填真实 key。 |

公开仓库允许保留 provider 的公开 API endpoint 和模型名，但不允许写真实 key、采购折扣、私有代理地址或真实服务器地址。

## 5. SQLite 路径变量

| 变量 | 示例占位值 | 说明 |
| --- | --- | --- |
| `DRAMORA_AUTH_DB_PATH` | `.local/dramora_auth.sqlite3` | Internal Auth SQLite 数据库路径。 |
| `DRAMORA_USAGE_LEDGER_DB_PATH` | `.local/dramora_usage_ledger.sqlite3` | Usage Ledger SQLite 数据库路径。 |
| `DRAMORA_OWNERSHIP_DB_PATH` | `.local/dramora_ownership.sqlite3` | Project / Session / Document ownership SQLite 数据库路径。 |

数据库文件要求：

- 只放在 `.local/`、`apps/api/.local/` 或私有部署目录；
- 不提交公开仓库；
- 不通过公开聊天或公开 issue 传递；
- 内部试运行前应有备份策略；
- 后续迁移服务器时单独写部署文档处理。

## 6. 未来 Token / Session Secret 预留

| 变量 | 示例占位值 | 说明 |
| --- | --- | --- |
| `DRAMORA_TOKEN_SECRET` | `change_me_before_internal_trial` | 未来 token 策略占位。 |
| `DRAMORA_SESSION_SECRET` | `change_me_before_internal_trial` | 未来 session 策略占位。 |

当前 token 生命周期、过期、刷新和权限中间件尚未生产化。这两个变量只是部署前准备占位，不代表正式 JWT / session 系统已经完成。

内部试运行前必须替换为私密值，并在部署文档中明确生成、轮换和保管方式。

## 7. 禁止提交内容

公开仓库禁止提交：

- 真实 `.env`；
- 真实 API Key；
- 真实员工账号；
- 真实密码；
- 真实 `password_hash`；
- 真实 token / session secret；
- SQLite 数据库文件；
- 真实上传文件；
- 真实导出文件；
- 真实客户剧本；
- provider 原始响应；
- 本机绝对路径；
- 真实服务器 IP 或域名。

## 8. 本地检查命令

提交前建议执行：

```bash
git status

git diff --stat

git diff --name-only

git ls-files | grep -E '(^|/)\.env($|\.|/)'

git ls-files | grep -E '\.(db|sqlite|sqlite3)$|^\.local/' || true

find . -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3"

grep -R "sk-[A-Za-z0-9]\|DEEPSEEK_API_KEY=.*[A-Za-z0-9]\{12,\}\|MIMO_API_KEY=.*[A-Za-z0-9]\{12,\}\|KIMI_API_KEY=.*[A-Za-z0-9]\{12,\}\|MINIMAX_API_KEY=.*[A-Za-z0-9]\{12,\}\|password_hash.*\$2\|BEGIN OPENSSH PRIVATE KEY\|/Users/" README.md README.zh-CN.md README.en.md docs apps/api/app apps/web/src tests/api .env.example | head -120
```

说明：

- grep 命中变量名、占位值、文档说明或 forbidden key 清单时要看上下文；
- 真正不能出现的是实际 key、真实私钥、真实本机路径、真实密码、真实 hash、真实客户内容；
- 不要为了让 grep 完全无输出而删除安全说明。

## 9. 部署阶段另开文档

服务器、域名、HTTPS、Nginx、CORS、token secret 轮换、数据库备份、日志轮转和权限中间件属于部署上线阶段。

当本地 Go / No-Go checklist 完成后，应新开：

```text
06｜部署上线｜服务器、域名、数据库、HTTPS 与内部试运行
```

在此之前不要把本地 `.env`、SQLite 数据库、上传文件、导出文件或临时脚本直接搬上云。
