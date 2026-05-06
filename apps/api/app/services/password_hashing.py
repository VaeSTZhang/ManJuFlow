import hashlib
import hmac
import secrets


PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 260_000
PASSWORD_HASH_SALT_BYTES = 16


def hash_password(password: str) -> str:
    normalized_password = password.strip()
    if not normalized_password:
        raise ValueError("password 不能为空。")

    salt_hex = secrets.token_hex(PASSWORD_HASH_SALT_BYTES)
    password_hash_hex = _derive_password_hash_hex(
        normalized_password,
        salt_hex,
        PASSWORD_HASH_ITERATIONS,
    )
    return f"{PASSWORD_HASH_ALGORITHM}${PASSWORD_HASH_ITERATIONS}${salt_hex}${password_hash_hex}"


def verify_password(password: str, password_hash: str) -> bool:
    normalized_password = password.strip()
    if not normalized_password:
        return False

    try:
        algorithm, iterations_text, salt_hex, expected_hash_hex = password_hash.split("$", maxsplit=3)
        if algorithm != PASSWORD_HASH_ALGORITHM:
            return False
        iterations = int(iterations_text)
        actual_hash_hex = _derive_password_hash_hex(normalized_password, salt_hex, iterations)
    except (AttributeError, TypeError, ValueError):
        return False

    return hmac.compare_digest(actual_hash_hex, expected_hash_hex)


def _derive_password_hash_hex(password: str, salt_hex: str, iterations: int) -> str:
    salt = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    ).hex()
