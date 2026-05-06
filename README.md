# Dramora｜剧作工坊

面向短剧创作的结构化剧本生成与文本改编工作台。

[English](README.en.md)

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646cff)
![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)
![Python](https://img.shields.io/badge/Backend-Python-3776ab)
![Status](https://img.shields.io/badge/Status-In%20Development-2563eb)
![License](https://img.shields.io/badge/License-No%20public%20license%20yet-b42318)

## 项目定位

Dramora｜剧作工坊 是一个面向短剧创作的剧本生成与文本改编工作台。当前聚焦“剧本创作生成”：从故事灵感、人物关系、电影剧本、小说或网文文本出发，生成适合短剧创作的结构化剧本。

当前产品不会把分镜、提示词、图片生成等后续流程放在主页重点位置。它们可以作为后续制作流程继续扩展，但现阶段优先服务编剧、短剧策划、内容团队和创作运营人员完成可编辑、可审阅、可交接的剧本文本。

## 当前核心能力

- 灵感生成短剧剧本；
- 电影剧本改编短剧本；
- 小说 / 网文改编短剧本；
- 长文本整理与短剧化改编；
- 剧本生成结果在线审看、编辑、复制和导出；
- TXT / JSON / DOCX 导出闭环；
- DeepSeek 三入口真实 LLM 小样本验收已完成；
- `context_options` 已用于 user / workspace / project / session 归属追踪；
- Usage Ledger 已完成 SQLite repository，并已接入剧本生成、文档导入预览、TXT / JSON / DOCX 导出链路；当前仅记录脱敏摘要，不记录完整文本、上传文件、模型原始响应或密钥；
- 后续可进入分镜、提示词和制作流程，但这些不是当前主页重点。

当前仍处于内部开发与部署前准备阶段，尚未进入服务器部署、生产上线或正式多人权限系统阶段。

## 当前产品主线

```text
登录
  → 剧本创作
  → 灵感生成 / 文本改编
  → 结构化短剧剧本
  → 在线编辑 / 导出
```

## 为什么是 Dramora

- 聚焦短剧剧本生成与改编；
- 面向编剧、短剧策划、内容团队和创作运营人员；
- 先完成可编辑、可审阅、可交接的剧本文本；
- 后续再扩展到分镜、提示词和制作资产；
- 公开仓库只保留可评审的工程结构、mock 能力和文档边界。

## 本地开发

ManJuFlow 是早期工程代号。当前公开仓库和本地工程目录统一使用 Dramora；脚本、后端包名、前端 package 名和 API 路径不因品牌名调整而重命名。

后端启动：

```bash
cd /path/to/Dramora
bash scripts/dev_api.sh
```

前端启动：

```bash
cd /path/to/Dramora/apps/web
npm run dev
```

后端测试：

```bash
cd /path/to/Dramora
python -m pytest tests/api
```

前端构建：

```bash
cd /path/to/Dramora/apps/web
npm run build
```

## 快速导航

- [English README](README.en.md)
- [中文完整说明](README.zh-CN.md)
- [本地开发文档](docs/LOCAL_DEV.md)
- [接口契约](docs/API_CONTRACT.md)
- [路线图](docs/MVP_ROADMAP.md)

## 使用声明 / 权利声明

当前公开仓库仅用于技术评审、项目展示和合作沟通。

当前暂未授予开源许可证。公开可见不等于开源授权。未经书面许可，不得商业使用、再分发、转授权或生产部署。

真实 API Key、`.env`、服务器地址、模型权重、客户剧本、员工数据、私有 workflow、私有 workflow registry、合作敏感资料不进入公开仓库。

构建产物、测试报告、上传文件、本地虚拟环境、`node_modules`、`.env` 与本地存储目录均应保持在 Git 忽略范围内。
