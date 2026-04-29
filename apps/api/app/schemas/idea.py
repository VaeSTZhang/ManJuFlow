from pydantic import BaseModel, Field


class IdeaInput(BaseModel):
    idea_text: str = Field(..., description="用户输入的灵感文本。")
    script_type: str = Field("短剧", description="剧本类型，例如短剧、漫剧、广告片、分镜脚本。")
    genre: str = Field("都市", description="内容类型，例如都市、悬疑、情感、职场、古风等。")
    episode_count: int = Field(1, ge=1, description="集数，必须大于等于 1。")
    episode_duration: str = Field("3-5分钟", description="单集时长。")
    target_platform: str = Field("短视频平台", description="目标发布平台。")
    tone: str = Field("节奏快、钩子强、反转明显", description="整体风格语气。")
    audience: str = Field("短剧观众", description="目标受众。")
    style_requirements: str | None = Field(None, description="额外风格要求。")
