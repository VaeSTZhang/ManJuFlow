import json
from pathlib import Path

from app.config import get_settings
from app.schemas.image_prompt import ImagePromptInput, ImagePromptItem, ImagePromptOutput
from app.services.llm_client import LLMClient
from app.services.text_cleaner import clean_chinese_spacing
from pydantic import ValidationError


NEGATIVE_PROMPT = (
    "low quality, blurry, bad anatomy, extra fingers, distorted face, watermark, text, logo"
)
NEGATIVE_PROMPT_ZH = (
    "低质量、模糊、人体结构错误、多余手指、脸部变形、水印、文字、logo, "
    "low quality, blurry, watermark"
)


def _strip_markdown_code_fence(raw_text: str) -> str:
    text = raw_text.strip()

    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def _extract_json_object(raw_text: str) -> str:
    start = raw_text.find("{")
    end = raw_text.rfind("}")

    if start == -1 or end == -1 or end < start:
        return raw_text

    return raw_text[start : end + 1]


def load_image_prompt_template(
    prompt_name: str = "storyboard_to_image_prompt_v1.md",
) -> str:
    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    prompt_path = prompts_dir / prompt_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Image prompt file not found: {prompt_name}")

    return prompt_path.read_text(encoding="utf-8")


def parse_image_prompt_llm_response(raw_text: str) -> ImagePromptOutput:
    if not raw_text or not raw_text.strip():
        raise ValueError("ImagePrompt LLM response is empty.")

    cleaned_text = _strip_markdown_code_fence(raw_text)
    json_text = _extract_json_object(cleaned_text)

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"ImagePrompt LLM response is not valid JSON: {exc}") from exc

    cleaned_data = clean_chinese_spacing(data)

    try:
        return ImagePromptOutput.model_validate(cleaned_data)
    except ValidationError as exc:
        raise ValueError(f"ImagePrompt LLM response does not match ImagePromptOutput schema: {exc}") from exc


def _get_source_visual_description(input_data: ImagePromptInput) -> str:
    if input_data.storyboard_text and input_data.storyboard_text.strip():
        return input_data.storyboard_text.strip()[:120]

    if input_data.storyboard_summary and input_data.storyboard_summary.strip():
        return input_data.storyboard_summary.strip()[:120]

    return "雨夜医院门口，男女主角在冷色车灯和雨幕中重逢。"


def _is_chinese_prompt_language(language: str) -> bool:
    return language.lower() == "zh"


def generate_image_prompt_mock(input_data: ImagePromptInput) -> ImagePromptOutput:
    load_image_prompt_template()

    source_description = _get_source_visual_description(input_data)
    use_chinese_prompt = _is_chinese_prompt_language(input_data.language)

    if use_chinese_prompt:
        prompt_summary = (
            "这是基于输入分镜生成的中文 mock 绘图 Prompt，用于验证“分镜到 AI 绘图 Prompt”"
            "服务层结构。当前输出包含稳定可追踪的中文镜头 Prompt 条目。"
        )
        positive_prompt_1 = (
            "电影写实风格，竖屏画面，雨夜医院门口，年轻女人撑着黑伞站在台阶上，"
            "年轻男人从深色轿车里下来，冷色车灯反射在湿漉漉的地面上，久别重逢的紧张情绪，"
            "中景，平视机位，面部细节清晰，强烈电影感明暗对比"
        )
        positive_prompt_2 = (
            "电影写实特写，黑伞边缘挂着雨滴，年轻女人在冷蓝色光线下压抑克制的表情，"
            "医院入口在背景中虚化，发丝被雨水打湿，情绪张力强，浅景深，面部结构干净自然，"
            "冷峻电影灯光"
        )
        negative_prompt = NEGATIVE_PROMPT_ZH
        notes_1 = "当前为中文 Prompt mock 输出；不要加入新角色或改变雨夜医院门口场景。"
        notes_2 = "当前为中文 Prompt mock 输出，用于验证多条 ImagePromptItem 的结构稳定性。"
    else:
        prompt_summary = (
            "This mock ImagePrompt output uses English prompts for validating the storyboard to AI image "
            "prompt service contract. The result contains stable and traceable shot prompt items."
        )
        positive_prompt_1 = (
            "cinematic realistic vertical frame, rainy night at a hospital entrance, "
            "young woman holding a black umbrella on the steps, young man stepping out "
            "of a dark car, cold headlights reflecting on wet pavement, tense reunion mood, "
            "medium shot, eye-level angle, detailed faces, dramatic contrast lighting"
        )
        positive_prompt_2 = (
            "cinematic realistic close-up, rain drops on a black umbrella edge, "
            "young woman's restrained expression under cold blue light, hospital entrance "
            "blurred in the background, wet hair strands, emotional tension, shallow depth "
            "of field, clean facial anatomy, moody film lighting"
        )
        negative_prompt = NEGATIVE_PROMPT
        notes_1 = "Current mock output uses English prompts. Do not add new characters or change the rainy hospital scene."
        notes_2 = "Current mock output uses English prompts for validating multiple ImagePromptItem records."

    return ImagePromptOutput(
        project_title=input_data.project_title,
        prompt_summary=prompt_summary,
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
                positive_prompt=positive_prompt_1,
                negative_prompt=negative_prompt,
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
                notes=notes_1,
            ),
            ImagePromptItem(
                prompt_id="P002",
                shot_id="S001_SH002",
                scene_id="S001",
                shot_number=2,
                scene_number=1,
                source_visual_description=source_description,
                positive_prompt=positive_prompt_2,
                negative_prompt=negative_prompt,
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
                notes=notes_2,
            ),
        ],
    )


def generate_image_prompt_llm(input_data: ImagePromptInput) -> ImagePromptOutput:
    prompt_template = load_image_prompt_template()
    input_json = json.dumps(input_data.model_dump(), ensure_ascii=False)
    messages = [
        {
            "role": "system",
            "content": prompt_template,
        },
        {
            "role": "user",
            "content": f"请根据以下输入生成结构化绘图 Prompt JSON：\n{input_json}",
        },
    ]

    content = LLMClient(provider=input_data.llm_provider, model=input_data.llm_model).chat(messages)
    return parse_image_prompt_llm_response(content)


def generate_image_prompt(input_data: ImagePromptInput) -> ImagePromptOutput:
    mode = get_settings().image_prompt_generation_mode.lower()

    if mode == "mock":
        return generate_image_prompt_mock(input_data)

    if mode == "llm":
        return generate_image_prompt_llm(input_data)

    raise ValueError("IMAGE_PROMPT_GENERATION_MODE only supports 'mock' or 'llm'.")
