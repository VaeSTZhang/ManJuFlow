from pydantic import BaseModel, Field


class CharacterProfile(BaseModel):
    name: str = Field(..., description="角色姓名。")
    role: str = Field(..., description="角色在故事中的身份或功能。")
    age: str = Field(..., description="角色年龄或年龄段。")
    personality: str = Field(..., description="角色性格特征。")
    arc: str = Field(..., description="角色在故事中的成长或变化弧线。")


class DialogueLine(BaseModel):
    character: str = Field(..., description="说出台词的角色。")
    line: str = Field(..., description="角色台词内容。")


class SceneScript(BaseModel):
    scene_number: int = Field(..., ge=1, description="场景编号，必须大于等于 1。")
    location: str = Field(..., description="场景发生地点。")
    time: str = Field(..., description="场景发生时间。")
    description: str = Field(..., description="场景剧情描述。")
    dialogues: list[DialogueLine] = Field(default_factory=list, description="场景内的对白列表。")
    visual_notes: str = Field(..., description="画面、镜头或视觉呈现说明。")
    emotion_curve: str = Field(..., description="场景情绪变化曲线。")


class EpisodeScript(BaseModel):
    episode_number: int = Field(..., ge=1, description="集数编号，必须大于等于 1。")
    title: str = Field(..., description="单集标题。")
    summary: str = Field(..., description="单集剧情概要。")
    hook: str = Field(..., description="单集钩子或悬念点。")
    scenes: list[SceneScript] = Field(default_factory=list, description="单集包含的场景列表。")


class ScriptOutput(BaseModel):
    project_title: str = Field(..., description="项目标题。")
    logline: str = Field(..., description="一句话故事梗概。")
    world_setting: str = Field(..., description="故事世界观或背景设定。")
    characters: list[CharacterProfile] = Field(default_factory=list, description="主要角色列表。")
    episodes: list[EpisodeScript] = Field(default_factory=list, description="分集剧本列表。")
