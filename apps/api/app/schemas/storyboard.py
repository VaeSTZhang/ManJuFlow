from pydantic import BaseModel, Field


class StoryboardInput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    script_text: str = Field(..., min_length=1, description="需要转分镜的剧本文本或结构化剧本摘要。")
    episode_number: int = Field(1, ge=1, description="集数编号，必须大于等于 1。")
    scene_number: int | None = Field(None, ge=1, description="指定场次编号，可选。")
    style: str = Field("短剧分镜", min_length=1, description="分镜风格。")
    target_platform: str = Field("短视频平台", min_length=1, description="目标发布平台。")
    visual_style: str = Field("现实主义、强情绪、电影感", min_length=1, description="整体视觉风格。")
    shot_count: int | None = Field(None, ge=1, description="期望镜头数量，可选。")
    extra_requirements: str | None = Field(None, description="额外分镜要求。")


class ShotStoryboard(BaseModel):
    shot_id: str = Field(..., min_length=1, description="镜头唯一标识，例如 S001_SH001。")
    shot_number: int = Field(..., ge=1, description="镜头编号，必须大于等于 1。")
    scene_number: int = Field(..., ge=1, description="所属场次编号，必须大于等于 1。")
    shot_type: str = Field(..., min_length=1, description="景别，例如远景、中景、近景、特写。")
    camera_angle: str = Field(..., min_length=1, description="机位角度，例如平视、俯拍、仰拍、侧拍。")
    camera_movement: str = Field(..., min_length=1, description="镜头运动，例如固定、推镜、拉镜、跟拍、摇镜。")
    subject: str = Field(..., min_length=1, description="画面主体。")
    action: str = Field(..., min_length=1, description="人物动作或事件动作。")
    environment: str = Field(..., min_length=1, description="场景环境。")
    lighting: str = Field(..., min_length=1, description="光影氛围。")
    emotion: str = Field(..., min_length=1, description="本镜头的情绪重点。")
    dialogue: str | None = Field(None, description="对白或旁白，可选。")
    duration_seconds: float | None = Field(None, gt=0, description="建议镜头时长，单位为秒，可选。")
    visual_description: str = Field(..., min_length=1, description="适合直接给绘图 Prompt 阶段使用的完整画面描述。")
    visual_notes: str = Field(..., min_length=1, description="视觉备注。")
    ai_image_prompt_hint: str = Field(..., min_length=1, description="后续转绘图 Prompt 的画面提示。")


class SceneStoryboard(BaseModel):
    scene_id: str = Field(..., min_length=1, description="场景唯一标识，例如 S001。")
    scene_number: int = Field(..., ge=1, description="场次编号，必须大于等于 1。")
    location: str = Field(..., min_length=1, description="场景地点。")
    time: str = Field(..., min_length=1, description="场景时间。")
    scene_summary: str = Field(..., min_length=1, description="场景摘要。")
    scene_conflict: str = Field(..., min_length=1, description="本场核心冲突。")
    shots: list[ShotStoryboard] = Field(..., min_length=1, description="本场景下的分镜镜头列表。")


class StoryboardOutput(BaseModel):
    project_title: str = Field(..., min_length=1, description="项目标题。")
    episode_number: int = Field(..., ge=1, description="集数编号，必须大于等于 1。")
    storyboard_summary: str = Field(..., min_length=1, description="分镜整体说明。")
    scenes: list[SceneStoryboard] = Field(..., min_length=1, description="分镜场景列表。")
