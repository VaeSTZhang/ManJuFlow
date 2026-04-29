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

## POST /api/storyboards/generate

用途：根据结构化剧本或剧本文本生成分镜结果。

当前说明：此接口当前使用 mock service，暂未接入真实 LLM、数据库或图片生成能力。

`scene_id`、`shot_id`、`visual_description` 用于后续“分镜 → AI 绘图 Prompt”的稳定衔接。

### 请求体字段

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `project_title` | string | 是 | 无 | 项目标题，非空 |
| `script_text` | string | 是 | 无 | 需要转分镜的剧本文本或结构化剧本摘要，非空 |

当前前端只传入 `project_title` 和 `script_text`。后端 `StoryboardInput` 还支持 `episode_number`、`scene_number`、`style`、`target_platform`、`visual_style`、`shot_count`、`extra_requirements` 等可选字段。

### 响应体核心字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `project_title` | string | 项目标题，非空 |
| `episode_number` | integer | 集数编号，必须大于等于 1 |
| `storyboard_summary` | string | 分镜整体说明，非空 |
| `scenes` | array | 分镜场景列表，至少 1 个 |

`scenes` 字段包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `scene_id` | string | 场景唯一标识，非空，例如 `S001`，用于后续流水线稳定引用 |
| `scene_number` | integer | 场次编号，必须大于等于 1 |
| `location` | string | 场景地点 |
| `time` | string | 场景时间 |
| `scene_summary` | string | 场景摘要 |
| `scene_conflict` | string | 本场核心冲突 |
| `shots` | array | 本场景下的分镜镜头列表，至少 1 个 |

`shots` 字段包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `shot_id` | string | 镜头唯一标识，非空，例如 `S001_SH001`，用于后续流水线稳定引用 |
| `shot_number` | integer | 镜头编号，必须大于等于 1 |
| `scene_number` | integer | 所属场次编号 |
| `shot_type` | string | 景别，例如远景、中景、近景、特写 |
| `camera_angle` | string | 机位角度，例如平视、俯拍、仰拍、侧拍 |
| `camera_movement` | string | 镜头运动，例如固定、推镜、拉镜、跟拍、摇镜 |
| `subject` | string | 画面主体 |
| `action` | string | 人物动作或事件动作 |
| `environment` | string | 场景环境 |
| `lighting` | string | 光影氛围 |
| `emotion` | string | 本镜头的情绪重点 |
| `dialogue` | string/null | 对白或旁白 |
| `duration_seconds` | number/null | 建议镜头时长，单位为秒；如果存在，必须大于 0 |
| `visual_description` | string | 适合直接给绘图 Prompt 阶段使用的完整画面描述，非空 |
| `visual_notes` | string | 视觉备注 |
| `ai_image_prompt_hint` | string | 后续转绘图 Prompt 的画面提示，非空 |

### curl 测试示例

```bash
curl -X POST "http://127.0.0.1:8000/api/storyboards/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_title": "测试短剧：雨夜重逢",
    "script_text": "第1集 第1场｜医院门口｜雨夜。暴雨中，林晚撑着黑伞站在医院门口，顾沉从车里下来，两人隔雨对视。顾沉：你终于肯回来了？林晚：我回来，不是为了见你。"
  }'
```

## 后续说明

后续会将当前 mock 逻辑替换为真实 LLM 调用层，并保持接口契约尽量稳定。
