from __future__ import annotations

import re
from dataclasses import dataclass


COMMON_PASSWORDS = {
    "password",
    "123456",
    "qwerty",
    "admin",
    "letmein",
    "welcome",
    "iloveyou",
    "password123",
}


@dataclass(frozen=True)
class StrengthReport:
    score: int
    label: str
    color: str
    suggestions: list[str]


def estimate_password_strength(password: str) -> StrengthReport:
    score = 0
    suggestions: list[str] = []
    password_lower = password.lower()

    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        suggestions.append("Увеличьте длину пароля минимум до 12 символов.")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        suggestions.append("Добавьте строчные буквы.")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        suggestions.append("Добавьте заглавные буквы.")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        suggestions.append("Добавьте цифры.")

    if re.search(r"[^A-Za-z0-9]", password):
        score += 1
    else:
        suggestions.append("Добавьте спецсимволы.")

    if password_lower in COMMON_PASSWORDS:
        score = 0
        suggestions = ["Пароль слишком распространенный. Используйте уникальный пароль."]

    if score <= 2:
        return StrengthReport(score=score, label="Слабый", color="#d7263d", suggestions=suggestions)
    if score <= 4:
        return StrengthReport(score=score, label="Средний", color="#f4a261", suggestions=suggestions)
    if score <= 6:
        return StrengthReport(score=score, label="Хороший", color="#2a9d8f", suggestions=suggestions)
    return StrengthReport(score=score, label="Отличный", color="#1d7a46", suggestions=suggestions)
