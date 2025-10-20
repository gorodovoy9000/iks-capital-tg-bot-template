import secrets
import string

import bcrypt


def generate_random_password(length=16):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def hash_password(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    return hashed_password


def generate_password_and_hash() -> tuple[str, str]:
    password = generate_random_password()
    hashed_password = hash_password(password)
    return password, hashed_password
