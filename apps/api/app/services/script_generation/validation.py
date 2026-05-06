from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput


class ScriptGenerationContractError(ValueError):
    pass


def resolve_target_episode_count(input_data: ShortDramaGenerationInput) -> int | None:
    if "target_episode_count" in input_data.model_fields_set:
        return _validate_resolved_target_episode_count(input_data.target_episode_count)

    adaptation_notes = input_data.adaptation_notes or {}
    if "target_episode_count" not in adaptation_notes:
        return None

    return _validate_resolved_target_episode_count(adaptation_notes.get("target_episode_count"))


def _validate_resolved_target_episode_count(value: object) -> int:
    if isinstance(value, bool):
        raise ScriptGenerationContractError("Invalid target_episode_count: must be a positive integer.")

    if isinstance(value, int):
        target = value
    elif isinstance(value, str) and value.strip().isdigit():
        target = int(value.strip())
    else:
        raise ScriptGenerationContractError("Invalid target_episode_count: must be a positive integer.")

    if target < 1:
        raise ScriptGenerationContractError("Invalid target_episode_count: must be a positive integer.")

    return target


def validate_target_episode_count_contract(
    input_data: ShortDramaGenerationInput,
    output: ShortDramaScriptOutput,
) -> ShortDramaScriptOutput:
    requested_count = resolve_target_episode_count(input_data)
    if requested_count is None:
        return output

    actual_episode_count = output.episode_count
    actual_episodes_length = len(output.episodes)
    expected_episode_numbers = list(range(1, requested_count + 1))
    actual_episode_numbers = [episode.episode_number for episode in output.episodes]

    if (
        actual_episode_count != requested_count
        or actual_episodes_length != requested_count
        or actual_episode_numbers != expected_episode_numbers
    ):
        raise ScriptGenerationContractError(
            "Generated script does not match requested target_episode_count: "
            f"requested={requested_count}, "
            f"episode_count={actual_episode_count}, "
            f"episodes={actual_episodes_length}, "
            f"episode_numbers={actual_episode_numbers}."
        )

    return output
