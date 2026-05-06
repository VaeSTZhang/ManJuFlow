PASSWORD_POLICY_MIN_LENGTH = 8


def check_internal_password_policy(password: str) -> dict[str, bool]:
    stripped_password = password.strip()
    min_length = len(stripped_password) >= PASSWORD_POLICY_MIN_LENGTH
    has_uppercase = any("A" <= character <= "Z" for character in stripped_password)
    has_lowercase = any("a" <= character <= "z" for character in stripped_password)
    has_digit = any("0" <= character <= "9" for character in stripped_password)

    return {
        "min_length": min_length,
        "has_uppercase": has_uppercase,
        "has_lowercase": has_lowercase,
        "has_digit": has_digit,
        "valid": min_length and has_uppercase and has_lowercase and has_digit,
    }


def validate_internal_password_policy(password: str) -> None:
    policy_result = check_internal_password_policy(password)

    if policy_result["valid"]:
        return

    failed_rules = [
        rule_name
        for rule_name in ("min_length", "has_uppercase", "has_lowercase", "has_digit")
        if not policy_result[rule_name]
    ]
    raise ValueError(f"密码不符合内部账号安全规则：{', '.join(failed_rules)}。")
