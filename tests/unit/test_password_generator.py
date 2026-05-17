from __future__ import annotations

import re

from utils.generators.password_generator import generate_password


def test_generate_password_length_and_charset() -> None:
    password = generate_password(length=20, use_lowercase=True, use_uppercase=True, use_digits=True, use_symbols=True)
    assert len(password) == 20
    assert re.search(r"[a-z]", password)
    assert re.search(r"[A-Z]", password)
    assert re.search(r"[0-9]", password)
    assert re.search(r"[^A-Za-z0-9]", password)
