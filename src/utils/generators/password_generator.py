from __future__ import annotations

import secrets
import string


def generate_password(
    length: int = 16,
    use_lowercase: bool = True,
    use_uppercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    pools = []
    if use_lowercase:
        pools.append(string.ascii_lowercase)
    if use_uppercase:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append("!@#$%^&*()-_=+[]{};:,.?/|")

    if not pools:
        raise ValueError("Выберите хотя бы один набор символов.")
    if length < len(pools):
        raise ValueError("Длина должна быть не меньше количества выбранных наборов.")

    password_chars = [secrets.choice(pool) for pool in pools]
    alphabet = "".join(pools)
    password_chars.extend(secrets.choice(alphabet) for _ in range(length - len(password_chars)))
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)
