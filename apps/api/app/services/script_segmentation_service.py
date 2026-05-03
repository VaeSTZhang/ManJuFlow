from app.schemas.script_segmentation import (
    ExistingScriptInput,
    ScriptSegment,
    ScriptSegmentationOutput,
)


CONTEXT_ISOLATION_NOTE = "Mock segmentation only uses the current input context and does not read other projects."


def _get_mock_source_text(input_data: ExistingScriptInput) -> str:
    if input_data.script_text:
        return input_data.script_text.strip()

    return f"Mock extracted text from upload source: {input_data.source_id}"


def _excerpt_text(text: str, start: int, length: int = 72) -> str:
    excerpt = text[start : start + length].strip()
    return excerpt or text[:length].strip() or "已有剧本文本片段"


def _build_segment_metadata(input_data: ExistingScriptInput) -> dict:
    return {
        "workspace_id": input_data.workspace_id,
        "user_id": input_data.user_id,
        "ai_account_id": input_data.ai_account_id,
        "source_id": input_data.source_id,
        "project_context_policy": "current_project_only",
    }


def generate_script_segmentation_mock(input_data: ExistingScriptInput) -> ScriptSegmentationOutput:
    source_text = _get_mock_source_text(input_data)
    first_excerpt = _excerpt_text(source_text, 0)
    second_excerpt = _excerpt_text(source_text, max(len(source_text) // 2, 0))
    segment_metadata = _build_segment_metadata(input_data)

    segments = [
        ScriptSegment(
            segment_id="SEG_001",
            episode_number=1,
            scene_number=1,
            segment_type=input_data.target_segment_level,
            title="开场冲突",
            original_text=first_excerpt,
            summary="主角进入关键情境，核心冲突被初步抛出。",
            characters=["主角", "对手角色"],
            location="主要场景",
            time_of_day="待定",
            conflict="主角想确认真相，对方试图回避或压制。",
            emotion="紧张、试探",
            visual_notes="适合用中近景建立人物关系和信息差。",
            dialogue_text=first_excerpt,
            estimated_duration_seconds=45.0,
            next_step_hint="可进入 Storyboard 阶段生成开场镜头拆解。",
            metadata=segment_metadata,
        ),
        ScriptSegment(
            segment_id="SEG_002",
            episode_number=1,
            scene_number=2,
            segment_type=input_data.target_segment_level,
            title="反转推进",
            original_text=second_excerpt,
            summary="冲突继续升级，人物动机和隐藏信息开始显露。",
            characters=["主角", "关键关系人"],
            location="延续场景",
            time_of_day="待定",
            conflict="主角发现新的疑点，关系人给出含糊回应。",
            emotion="压迫、悬疑",
            visual_notes="适合用特写和过肩镜头强化反转前的停顿。",
            dialogue_text=second_excerpt,
            estimated_duration_seconds=45.0,
            next_step_hint="可进入 Storyboard 阶段生成反转推进镜头。",
            metadata=segment_metadata,
        ),
    ]

    return ScriptSegmentationOutput(
        project_title=input_data.project_title,
        segmentation_summary="这是已有剧本切分 mock 结果，用于验证 Script Segmentation 数据协议和上下文隔离边界。",
        segment_count=len(segments),
        segments=segments,
        source_id=input_data.source_id,
        workspace_id=input_data.workspace_id,
        user_id=input_data.user_id,
        ai_account_id=input_data.ai_account_id,
        metadata={
            "source_type": input_data.source_type,
            "target_segment_level": input_data.target_segment_level,
            "language": input_data.language,
            "generation_mode": "mock",
            "context_isolation_note": CONTEXT_ISOLATION_NOTE,
        },
    )


def generate_script_segmentation(input_data: ExistingScriptInput) -> ScriptSegmentationOutput:
    return generate_script_segmentation_mock(input_data)
