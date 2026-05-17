from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import warnings

try:
    from pysqlcipher3 import dbapi2 as sqlcipher_db  # type: ignore

    SQLCIPHER_AVAILABLE = True
except ImportError:
    try:
        from sqlcipher3 import dbapi2 as sqlcipher_db  # type: ignore

        SQLCIPHER_AVAILABLE = True
    except ImportError:
        import sqlite3 as sqlcipher_db  # type: ignore

        SQLCIPHER_AVAILABLE = False
        warnings.warn(
            "SQLCipher driver is unavailable. Falling back to sqlite3 (unencrypted database).",
            RuntimeWarning,
            stacklevel=1,
        )


class DatabaseError(RuntimeError):
    pass


class DatabaseManager:
    def __init__(self, db_path: Path, db_key: bytes, kdf_iterations: int) -> None:
        self._db_path = db_path
        self._db_key = db_key
        self._kdf_iterations = kdf_iterations
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> Any:
        require_sqlcipher = os.environ.get("SPM_REQUIRE_SQLCIPHER", "0") == "1"
        if require_sqlcipher and not SQLCIPHER_AVAILABLE:
            raise DatabaseError(
                "SQLCipher is required (SPM_REQUIRE_SQLCIPHER=1), but no SQLCipher driver is available."
            )

        conn = sqlcipher_db.connect(str(self._db_path))
        conn.row_factory = sqlcipher_db.Row
        cursor = conn.cursor()

        if SQLCIPHER_AVAILABLE:
            key_literal = f"x'{self._db_key.hex()}'"
            cursor.execute(f'PRAGMA key = "{key_literal}";')
            cursor.execute(f"PRAGMA kdf_iter = {self._kdf_iterations};")
            cursor.execute("PRAGMA cipher_memory_security = ON;")
            cursor.execute("PRAGMA journal_mode = WAL;")

        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("SELECT count(*) FROM sqlite_master;")
        return conn

    def initialize_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    username_enc TEXT NOT NULL,
                    password_enc TEXT NOT NULL,
                    url_enc TEXT NOT NULL,
                    notes_enc TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_entries_category_title
                ON entries(category, title)
                """
            )

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self.connect() as conn:
            conn.execute(query, params)
            conn.commit()

    def insert_and_get_id(self, query: str, params: tuple[Any, ...] = ()) -> int:
        with self.connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return int(cursor.lastrowid)

    def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> Any:
        with self.connect() as conn:
            row = conn.execute(query, params).fetchone()
        return row

    def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[Any]:
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return list(rows)
