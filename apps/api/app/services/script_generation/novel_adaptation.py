import json
from pathlib import Path

from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript
from app.schemas.script_generation import (
    AdaptationNotes,
    ShortDramaGenerationInput,
    ShortDramaScriptOutput,
)
from app.services.llm_client import LLMClient
from app.services.script_generation.metadata import build_script_generation_metadata
from app.services.text_cleaner import clean_chinese_spacing


NOVEL_PROMPT_TEMPLATE_NAME = "novel_to_short_drama_v1.md"


def load_novel_prompt_template(
    template_name: str = NOVEL_PROMPT_TEMPLATE_NAME,
) -> str:
    prompts_dir = Path(__file__).resolve().parents[2] / "prompts"
    prompt_path = prompts_dir / template_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Novel adaptation prompt file not found: {template_name}")

    return prompt_path.read_text(encoding="utf-8")


def _build_novel_adaptation_characters() -> list[CharacterProfile]:
    return [
        CharacterProfile(
            name="沈南星",
            role="女主角，发现母亲日记的年轻编剧",
            age="25",
            personality="敏感、执拗、观察细致",
            arc="从逃避母亲旧事到主动揭开舞台事故真相。",
        ),
        CharacterProfile(
            name="顾闻舟",
            role="旧剧场管理员，掌握事故线索",
            age="32",
            personality="沉默、谨慎、内心有愧",
            arc="从隐瞒真相到帮助沈南星还原当年事故。",
        ),
    ]


def _build_novel_adaptation_episode(episode_number: int) -> EpisodeScript:
    secret_items = ["母亲日记", "掌声录音", "后台钥匙", "旧节目单", "断裂奖杯"]
    secret_item = secret_items[(episode_number - 1) % len(secret_items)]

    return EpisodeScript(
        episode_number=episode_number,
        title=f"第{episode_number}集：{secret_item}里的秘密",
        summary=(
            f"沈南星根据小说式叙事中的内心线索展开行动，"
            f"通过“{secret_item}”把母亲旧事转化为可见的舞台冲突。"
        ),
        hook=f"{secret_item}揭开一段被隐藏的舞台事故真相，顾闻舟说出一句只有日记里才有的话。",
        scenes=[
            SceneScript(
                scene_number=1,
                location="旧剧场后台",
                time="傍晚",
                description=(
                    f"沈南星在后台找到{secret_item}，把小说中的内心疑问转化为当面对质。"
                    "顾闻舟阻止她继续翻找，两人在破旧幕布前爆发冲突。"
                ),
                dialogues=[
                    DialogueLine(
                        character="沈南星",
                        line=f"这个{secret_item}，为什么会和我妈的日记放在一起？",
                    ),
                    DialogueLine(
                        character="顾闻舟",
                        line="有些掌声，不是给演员的，是给沉默的人看的。",
                    ),
                ],
                visual_notes=(
                    "竖屏近景拍沈南星握紧线索物件，反打顾闻舟压低声音阻止，"
                    "旧幕布和昏黄侧光把人物关系转成可见冲突。"
                ),
                emotion_curve="疑惑→追问→情绪揭露",
            )
        ],
    )


def generate_novel_adaptation_mock(
    input_data: ShortDramaGenerationInput,
) -> ShortDramaScriptOutput:
    if input_data.source_mode != "novel":
        raise ValueError("generate_novel_adaptation_mock only supports source_mode='novel'.")

    load_novel_prompt_template()

    project_title = input_data.project_title or "掌声背后的日记"
    episode_count = input_data.target_episode_count
    episodes = [
        _build_novel_adaptation_episode(episode_number)
        for episode_number in range(1, episode_count + 1)
    ]
    metadata = build_script_generation_metadata(input_data)
    metadata.update(
        {
            "prompt_template_name": NOVEL_PROMPT_TEMPLATE_NAME,
        }
    )

    return ShortDramaScriptOutput(
        project_title=project_title,
        source_mode="novel",
        logline="年轻编剧在旧书店发现母亲日记，追查一场被掌声掩盖的舞台事故真相。",
        world_setting="现代都市中的旧书店、废弃剧场和小型话剧团交织成悬疑情感世界。",
        characters=_build_novel_adaptation_characters(),
        adaptation_notes=AdaptationNotes(
            source_mode="novel",
            adaptation_strategy=(
                "将小说中的心理描写转化为沈南星寻找日记线索的动作、对白和场景冲突，"
                "用旧剧场和掌声录音承载人物关系与母女心结。"
            ),
            preserved_elements=[
                "旧书店发现母亲日记",
                "母女关系和未解心结",
                "舞台事故真相",
            ],
            changed_elements=[
                "压缩书店背景描写",
                "合并旁支人物",
                "将内心独白外化为与顾闻舟的对峙",
            ],
            short_drama_hooks=[
                "每集揭开一页日记",
                "掌声录音中混入母亲求救声",
                "顾闻舟逐步暴露隐藏关系",
            ],
            risk_notes=[
                "需确认原始小说、网文或故事文本的合法改编授权。",
                "当前输出为 mock 改编草案，需人工确认。",
            ],
        ),
        episode_count=episode_count,
        episodes=episodes,
        metadata=metadata,
    )


def generate_novel_adaptation_llm(
    input_data: ShortDramaGenerationInput,
) -> ShortDramaScriptOutput:
    if input_data.source_mode != "novel":
        raise ValueError("generate_novel_adaptation_llm only supports source_mode='novel'.")

    source_text = (input_data.source_text or "").strip()
    if not source_text:
        raise ValueError("source_mode='novel' requires source_text.")

    prompt_template = load_novel_prompt_template()
    input_payload = input_data.model_dump()
    input_payload["source_text"] = source_text
    input_json = json.dumps(input_payload, ensure_ascii=False)
    messages = [
        {
            "role": "system",
            "content": prompt_template,
        },
        {
            "role": "user",
            "content": f"请根据以下输入生成结构化小说改编短剧 JSON：\n{input_json}",
        },
    ]

    provider = input_data.ai_options.provider if input_data.ai_options else None
    model = input_data.ai_options.model if input_data.ai_options else None
    content = LLMClient(provider=provider, model=model).chat(messages)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response was not valid JSON.") from exc

    cleaned_data = clean_chinese_spacing(data)

    try:
        output = ShortDramaScriptOutput.model_validate(cleaned_data)
    except ValueError as exc:
        raise ValueError("LLM response did not match ShortDramaScriptOutput schema.") from exc

    metadata = {
        **output.metadata,
        **build_script_generation_metadata(input_data, generation_mode="llm"),
        "prompt_template_name": NOVEL_PROMPT_TEMPLATE_NAME,
    }
    source_title = input_data.metadata.get("source_title")
    if source_title:
        metadata["source_title"] = source_title

    return output.model_copy(update={"metadata": metadata})
