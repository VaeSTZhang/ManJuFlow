import json
from pathlib import Path

from app.config import get_settings
from app.schemas.idea import IdeaInput
from app.schemas.script import (
    CharacterProfile,
    DialogueLine,
    EpisodeScript,
    SceneScript,
    ScriptOutput,
)
from app.services.llm_client import LLMClient
from app.services.text_cleaner import clean_chinese_spacing


def load_prompt_template(prompt_name: str = "idea_to_script_v1.md") -> str:
    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    prompt_path = prompts_dir / prompt_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_name}")

    return prompt_path.read_text(encoding="utf-8")


def generate_script_mock(input_data: IdeaInput) -> ScriptOutput:
    load_prompt_template()

    title_seed = input_data.idea_text.strip()[:12] or input_data.genre
    project_title = f"{input_data.genre}{input_data.script_type}：{title_seed}"

    return ScriptOutput(
        project_title=project_title,
        logline=f"一个围绕“{input_data.idea_text.strip()}”展开的{input_data.genre}{input_data.script_type}，用{input_data.tone}的方式制造持续追看动力。",
        world_setting=f"故事发生在当代都市短视频语境下，人物关系紧凑，冲突适合{input_data.episode_duration}的{input_data.script_type}节奏。",
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


def generate_script_with_llm(input_data: IdeaInput) -> ScriptOutput:
    prompt_template = load_prompt_template()
    input_json = json.dumps(input_data.model_dump(), ensure_ascii=False)
    messages = [
        {
            "role": "system",
            "content": prompt_template,
        },
        {
            "role": "user",
            "content": f"请根据以下输入生成结构化剧本 JSON：\n{input_json}",
        },
    ]

    content = LLMClient().chat(messages)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response was not valid JSON.") from exc

    cleaned_data = clean_chinese_spacing(data)

    try:
        return ScriptOutput.model_validate(cleaned_data)
    except ValueError as exc:
        raise ValueError("LLM response did not match ScriptOutput schema.") from exc


def generate_script(input_data: IdeaInput) -> ScriptOutput:
    mode = get_settings().script_generation_mode.lower()

    if mode == "mock":
        return generate_script_mock(input_data)

    if mode == "llm":
        return generate_script_with_llm(input_data)

    raise ValueError("SCRIPT_GENERATION_MODE only supports 'mock' or 'llm'.")
