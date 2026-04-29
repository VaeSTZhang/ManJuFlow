from pathlib import Path

from app.schemas.image_prompt import ImagePromptInput, ImagePromptItem, ImagePromptOutput


NEGATIVE_PROMPT = (
    "low quality, blurry, bad anatomy, extra fingers, distorted face, watermark, text, logo"
)


def load_image_prompt_template(
    prompt_name: str = "storyboard_to_image_prompt_v1.md",
) -> str:
    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    prompt_path = prompts_dir / prompt_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Image prompt file not found: {prompt_name}")

    return prompt_path.read_text(encoding="utf-8")


def _get_source_visual_description(input_data: ImagePromptInput) -> str:
    if input_data.storyboard_text and input_data.storyboard_text.strip():
        return input_data.storyboard_text.strip()[:120]

    if input_data.storyboard_summary and input_data.storyboard_summary.strip():
        return input_data.storyboard_summary.strip()[:120]

    return "雨夜医院门口，男女主角在冷色车灯和雨幕中重逢。"


def generate_image_prompt_mock(input_data: ImagePromptInput) -> ImagePromptOutput:
    load_image_prompt_template()

    source_description = _get_source_visual_description(input_data)

    return ImagePromptOutput(
        project_title=input_data.project_title,
        prompt_summary=(
            "这是基于输入分镜生成的 mock 绘图 Prompt，用于验证“分镜到 AI 绘图 Prompt”"
            "服务层结构。当前输出包含稳定可追踪的镜头 Prompt 条目。"
        ),
        target_model=input_data.target_model,
        aspect_ratio=input_data.aspect_ratio,
        style_preset=input_data.style_preset,
        items=[
            ImagePromptItem(
                prompt_id="P001",
                shot_id="S001_SH001",
                scene_id="S001",
                shot_number=1,
                scene_number=1,
                source_visual_description=source_description,
                positive_prompt=(
                    "cinematic realistic vertical frame, rainy night at a hospital entrance, "
                    "young woman holding a black umbrella on the steps, young man stepping out "
                    "of a dark car, cold headlights reflecting on wet pavement, tense reunion mood, "
                    "medium shot, eye-level angle, detailed faces, dramatic contrast lighting"
                ),
                negative_prompt=NEGATIVE_PROMPT,
                style_preset=input_data.style_preset,
                aspect_ratio=input_data.aspect_ratio,
                camera_language="中景，平视机位，雨幕作为前景，两人隔着台阶和车灯对视。",
                lighting="冷色雨夜环境光与车灯交错，湿地反光强化压抑氛围。",
                color_palette="蓝灰冷色为主，少量车灯白光和暗红尾灯点缀。",
                character_consistency="保持男女主角年龄、发型、服装和克制表情的一致性。",
                environment="雨夜医院门口，台阶、玻璃门、湿滑路面和停靠车辆清晰可见。",
                composition="竖幅构图，两人分居画面两侧，雨幕和车灯形成视觉分隔。",
                model_hint=f"{input_data.target_model} image generation, prioritize realistic cinematic detail",
                seed=None,
                notes="Mock 输出，不调用真实 LLM；不要加入新角色或改变雨夜医院门口场景。",
            ),
            ImagePromptItem(
                prompt_id="P002",
                shot_id="S001_SH002",
                scene_id="S001",
                shot_number=2,
                scene_number=1,
                source_visual_description=source_description,
                positive_prompt=(
                    "cinematic realistic close-up, rain drops on a black umbrella edge, "
                    "young woman's restrained expression under cold blue light, hospital entrance "
                    "blurred in the background, wet hair strands, emotional tension, shallow depth "
                    "of field, clean facial anatomy, moody film lighting"
                ),
                negative_prompt=NEGATIVE_PROMPT,
                style_preset=input_data.style_preset,
                aspect_ratio=input_data.aspect_ratio,
                camera_language="近景特写，焦点落在女主克制的表情和伞沿雨滴上。",
                lighting="冷蓝环境光从侧面掠过面部，背景医院灯光虚化。",
                color_palette="冷蓝、灰黑和少量暖白灯光形成压抑对比。",
                character_consistency="延续女主黑伞、克制神情、现实主义服装和雨夜湿发细节。",
                environment="医院入口背景虚化，雨滴、伞面和湿冷空气作为主要环境元素。",
                composition="面部位于画面上三分之一，伞沿形成前景斜线，引导视线到眼神。",
                model_hint=f"{input_data.target_model} image generation, emphasize facial realism and rain details",
                seed=None,
                notes="Mock 输出，用于验证多条 ImagePromptItem 的结构稳定性。",
            ),
        ],
    )


def generate_image_prompt(input_data: ImagePromptInput) -> ImagePromptOutput:
    return generate_image_prompt_mock(input_data)
