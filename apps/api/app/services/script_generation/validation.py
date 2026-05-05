from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput


class ScriptGenerationContractError(ValueError):
    pass


def validate_target_episode_count_contract(
    input_data: ShortDramaGenerationInput,
    output: ShortDramaScriptOutput,
) -> ShortDramaScriptOutput:
    if "target_episode_count" not in input_data.model_fields_set:
        return output

    requested_count = input_data.target_episode_count
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
