from pathlib import Path

from app.config import get_settings
from app.schemas.storyboard import (
    SceneStoryboard,
    ShotStoryboard,
    StoryboardInput,
    StoryboardOutput,
)


def load_storyboard_prompt_template(
    prompt_name: str = "script_to_storyboard_v1.md",
) -> str:
    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    prompt_path = prompts_dir / prompt_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Storyboard prompt file not found: {prompt_name}")

    return prompt_path.read_text(encoding="utf-8")


def generate_storyboard_mock(input_data: StoryboardInput) -> StoryboardOutput:
    load_storyboard_prompt_template()

    scene_number = input_data.scene_number or 1
    scene_id = f"S{scene_number:03d}"
    script_excerpt = input_data.script_text.strip()[:48] or "输入剧本"

    return StoryboardOutput(
        project_title=input_data.project_title,
        episode_number=input_data.episode_number,
        storyboard_summary=(
            f"这是基于输入剧本生成的 mock 分镜，用于验证“剧本到分镜”服务层结构。"
            f"当前参考内容为“{script_excerpt}”，整体风格偏向{input_data.visual_style}。"
        ),
        scenes=[
            SceneStoryboard(
                scene_id=scene_id,
                scene_number=scene_number,
                location="主要冲突发生地点",
                time="傍晚",
                scene_summary="主角进入关键场景，发现局势和预期不同，冲突逐步升级。",
                scene_conflict="主角想确认真相，对方试图回避或压制，双方在信息差中形成对峙。",
                shots=[
                    ShotStoryboard(
                        shot_id=f"{scene_id}_SH001",
                        shot_number=1,
                        scene_number=scene_number,
                        shot_type="远景",
                        camera_angle="平视",
                        camera_movement="固定",
                        subject="主角和场景入口",
                        action="主角停在入口处，观察现场人物的位置和反应。",
                        environment="空间较空，远处有人低声交谈，入口与核心人物之间形成明显距离。",
                        lighting="傍晚冷光从窗边压进室内，环境略显紧张。",
                        emotion="警觉、迟疑",
                        dialogue="旁白：她意识到，这场见面从一开始就不简单。",
                        duration_seconds=4,
                        visual_description=(
                            "傍晚冷光压进空旷室内，主角站在场景入口处观察远处低声交谈的人群，"
                            "入口与核心人物之间保留明显距离，画面突出孤立感和紧张气氛。"
                        ),
                        visual_notes="用远景交代空间关系，让主角显得孤立，为后续冲突建立压迫感。",
                        ai_image_prompt_hint=(
                            "现实主义短剧画面，傍晚室内远景，主角站在入口处观察现场，"
                            "冷色光影，紧张氛围，电影感构图"
                        ),
                    ),
                    ShotStoryboard(
                        shot_id=f"{scene_id}_SH002",
                        shot_number=2,
                        scene_number=scene_number,
                        shot_type="中景",
                        camera_angle="过肩",
                        camera_movement="推镜",
                        subject="主角和对峙对象",
                        action="主角向前一步发问，对方停顿后避开视线。",
                        environment="桌面上散落着文件或手机，暗示关键信息被隐藏。",
                        lighting="主角面部有侧光，对方半张脸落在阴影里。",
                        emotion="试探、压迫",
                        dialogue="主角：你刚才说的那句话，到底是什么意思？",
                        duration_seconds=5,
                        visual_description=(
                            "中景过肩构图中，主角向前一步逼问对峙对象，对方停顿并避开视线，"
                            "桌面散落文件和手机，侧光照亮主角面部，对方半张脸藏在阴影里。"
                        ),
                        visual_notes="过肩构图突出双方距离，推镜加强质问的压迫感。",
                        ai_image_prompt_hint=(
                            "短剧中景过肩镜头，主角质问对方，桌面有文件和手机，"
                            "侧光与阴影对比，情绪紧绷，适合 AI 绘图"
                        ),
                    ),
                    ShotStoryboard(
                        shot_id=f"{scene_id}_SH003",
                        shot_number=3,
                        scene_number=scene_number,
                        shot_type="特写",
                        camera_angle="侧拍",
                        camera_movement="切镜",
                        subject="对峙对象的眼神和手部动作",
                        action="对方手指按住手机屏幕，眼神闪躲，露出破绽。",
                        environment="背景被虚化，只保留手机屏幕反光和人物表情。",
                        lighting="手机微光映在手指和下颌，制造秘密即将暴露的感觉。",
                        emotion="心虚、紧张、反转前的停顿",
                        dialogue="对方：你最好别继续查下去。",
                        duration_seconds=4,
                        visual_description=(
                            "特写镜头聚焦对峙对象闪躲的眼神和按住手机屏幕的手指，"
                            "背景虚化，只保留手机屏幕反光与面部边缘冷光，暗示秘密即将暴露。"
                        ),
                        visual_notes="特写聚焦手部和眼神，作为信息反转的视觉钩子。",
                        ai_image_prompt_hint=(
                            "电影感特写，人物手指按住手机屏幕，眼神闪躲，背景虚化，"
                            "手机冷光照亮面部边缘，悬疑紧张情绪"
                        ),
                    ),
                ],
            )
        ],
    )


def generate_storyboard(input_data: StoryboardInput) -> StoryboardOutput:
    mode = get_settings().storyboard_generation_mode.lower()

    if mode == "mock":
        return generate_storyboard_mock(input_data)

    if mode == "llm":
        # TODO: 接入真实 LLM 后，在这里调用剧本转分镜模型链路，并补充 JSON 解析与 Schema 校验修复。
        return generate_storyboard_mock(input_data)

    raise ValueError("STORYBOARD_GENERATION_MODE only supports 'mock' or 'llm'.")
