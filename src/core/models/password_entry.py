from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PasswordEntry:
    entry_id: int | None
    category: str
    title: str
    username: str
    password: str
    url: str
    notes: str
    created_at: str | None = None
    updated_at: str | None = None
