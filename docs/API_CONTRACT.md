# ManJuFlow｜漫剧流 API Contract

当前后端服务地址：

```text
http://127.0.0.1:8000
```

## GET /health

用途：检查后端服务是否正常运行。

返回示例：

```json
{
  "status": "ok",
  "stage": "mvp-idea-to-script"
}
```

## POST /api/scripts/generate

用途：根据用户输入的灵感信息生成结构化短剧剧本结果。

当前说明：此接口目前为 mock 版本，暂未接入真实 LLM。

### 请求体字段

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `idea_text` | string | 是 | 无 | 用户输入的灵感文本 |
| `script_type` | string | 否 | `短剧` | 剧本类型，例如短剧、漫剧、广告片、分镜脚本 |
| `genre` | string | 否 | `都市` | 内容类型，例如都市、悬疑、情感、职场、古风等 |
| `episode_count` | integer | 否 | `1` | 集数，必须大于等于 1 |
| `episode_duration` | string | 否 | `3-5分钟` | 单集时长 |
| `target_platform` | string | 否 | `短视频平台` | 目标发布平台 |
| `tone` | string | 否 | `节奏快、钩子强、反转明显` | 整体风格语气 |
| `audience` | string | 否 | `短剧观众` | 目标受众 |
| `style_requirements` | string/null | 否 | `null` | 额外风格要求 |

### 响应体字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `project_title` | string | 项目标题 |
| `logline` | string | 一句话故事梗概 |
| `world_setting` | string | 故事世界观或背景设定 |
| `characters` | array | 主要角色列表 |
| `episodes` | array | 分集剧本列表 |

`characters` 字段包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 角色姓名 |
| `role` | string | 角色在故事中的身份或功能 |
| `age` | string | 角色年龄或年龄段 |
| `personality` | string | 角色性格特征 |
| `arc` | string | 角色成长或变化弧线 |

`episodes` 字段包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `episode_number` | integer | 集数编号 |
| `title` | string | 单集标题 |
| `summary` | string | 单集剧情概要 |
| `hook` | string | 单集钩子或悬念点 |
| `scenes` | array | 单集包含的场景列表 |

`scenes` 字段包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `scene_number` | integer | 场景编号 |
| `location` | string | 场景发生地点 |
| `time` | string | 场景发生时间 |
| `description` | string | 场景剧情描述 |
| `dialogues` | array | 场景内的对白列表 |
| `visual_notes` | string | 画面、镜头或视觉呈现说明 |
| `emotion_curve` | string | 场景情绪变化曲线 |

`dialogues` 字段包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `character` | string | 说出台词的角色 |
| `line` | string | 角色台词内容 |

### curl 测试示例

```bash
curl -X POST http://127.0.0.1:8000/api/scripts/generate \
  -H "Content-Type: application/json" \
  -d '{"idea_text":"一个普通女孩发现公司老板正在隐藏一个巨大秘密","script_type":"短剧","genre":"都市"}'
```

## 后续说明

后续会将当前 mock 逻辑替换为真实 LLM 调用层，并保持接口契约尽量稳定。
