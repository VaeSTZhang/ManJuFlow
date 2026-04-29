from fastapi import APIRouter

from app.schemas.idea import IdeaInput
from app.schemas.script import (
    CharacterProfile,
    DialogueLine,
    EpisodeScript,
    SceneScript,
    ScriptOutput,
)


router = APIRouter(prefix="/api/scripts", tags=["scripts"])


@router.post("/generate", response_model=ScriptOutput)
def generate_script(idea: IdeaInput) -> ScriptOutput:
    title_seed = idea.idea_text.strip()[:12] or idea.genre
    project_title = f"{idea.genre}{idea.script_type}：{title_seed}"

    return ScriptOutput(
        project_title=project_title,
        logline=f"一个围绕“{idea.idea_text.strip()}”展开的{idea.genre}{idea.script_type}，用{idea.tone}的方式制造持续追看动力。",
        world_setting=f"故事发生在当代都市短视频语境下，人物关系紧凑，冲突适合{idea.episode_duration}的{idea.script_type}节奏。",
        characters=[
            CharacterProfile(
                name="林夏",
                role="主角",
                age="26",
                personality="敏感但行动力强，遇到压力时会快速做决定。",
                arc="从被动卷入冲突，到主动掌控局面并完成自我证明。",
            ),
            CharacterProfile(
                name="周明远",
                role="关键对手",
                age="32",
                personality="冷静、强势，擅长隐藏真实目的。",
                arc="从掌控局面的幕后推手，逐渐被主角识破并暴露弱点。",
            ),
        ],
        episodes=[
            EpisodeScript(
                episode_number=1,
                title="意外开局",
                summary="林夏因为一个看似普通的灵感线索，被卷入一场关系和利益交织的冲突。",
                hook="林夏发现，真正推动事件发生的人就在她身边。",
                scenes=[
                    SceneScript(
                        scene_number=1,
                        location="公司会议室",
                        time="傍晚",
                        description="林夏提出创意后，现场气氛突然变得紧张，周明远的反应暴露出异常。",
                        dialogues=[
                            DialogueLine(character="林夏", line="这个故事的核心，不只是反转，而是谁在操控反转。"),
                            DialogueLine(character="周明远", line="有些答案太早说出来，观众就不会继续看了。"),
                        ],
                        visual_notes="近景捕捉林夏的迟疑，切到周明远停顿的手部动作，制造悬念。",
                        emotion_curve="平静开场，迅速升温，结尾留下不安和疑问。",
                    )
                ],
            )
        ],
    )
