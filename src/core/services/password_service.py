from __future__ import annotations

from core.crypto.aes_gcm import AesGcmCipher
from core.database.db_manager import DatabaseManager
from core.models.password_entry import PasswordEntry
from core.services.audit_service import AuditService


DEFAULT_CATEGORIES = ("Соцсети", "Банки", "Работа", "Личное")


class PasswordService:
    def __init__(self, db_manager: DatabaseManager, data_key: bytes, audit: AuditService) -> None:
        self._db = db_manager
        self._cipher = AesGcmCipher(data_key)
        self._audit = audit

    def list_entries(self, category: str | None = None, query: str | None = None) -> list[PasswordEntry]:
        filters = []
        params: list[str] = []

        if category and category != "Все":
            filters.append("category = ?")
            params.append(category)
        if query:
            filters.append("LOWER(title) LIKE ?")
            params.append(f"%{query.lower()}%")

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        rows = self._db.fetchall(
            f"""
            SELECT id, category, title, username_enc, password_enc, url_enc, notes_enc, created_at, updated_at
            FROM entries
            {where_clause}
            ORDER BY title COLLATE NOCASE
            """,
            tuple(params),
        )
        return [self._row_to_entry(row) for row in rows]

    def get_entry(self, entry_id: int) -> PasswordEntry | None:
        row = self._db.fetchone(
            """
            SELECT id, category, title, username_enc, password_enc, url_enc, notes_enc, created_at, updated_at
            FROM entries
            WHERE id = ?
            """,
            (entry_id,),
        )
        if not row:
            return None
        return self._row_to_entry(row)

    def create_entry(self, entry: PasswordEntry) -> int:
        payload = self._to_encrypted(entry)
        entry_id = self._db.insert_and_get_id(
            """
            INSERT INTO entries (
                category, title, username_enc, password_enc, url_enc, notes_enc
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.category,
                payload.title,
                payload.username,
                payload.password,
                payload.url,
                payload.notes,
            ),
        )
        self._audit.log_record_action("created", entry_id)
        return entry_id

    def update_entry(self, entry_id: int, entry: PasswordEntry) -> None:
        payload = self._to_encrypted(entry)
        self._db.execute(
            """
            UPDATE entries
            SET category = ?,
                title = ?,
                username_enc = ?,
                password_enc = ?,
                url_enc = ?,
                notes_enc = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                payload.category,
                payload.title,
                payload.username,
                payload.password,
                payload.url,
                payload.notes,
                entry_id,
            ),
        )
        self._audit.log_record_action("updated", entry_id)

    def delete_entry(self, entry_id: int) -> None:
        self._db.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self._audit.log_record_action("deleted", entry_id)

    def _to_encrypted(self, entry: PasswordEntry) -> PasswordEntry:
        return PasswordEntry(
            entry_id=entry.entry_id,
            category=entry.category,
            title=entry.title,
            username=self._cipher.encrypt_text(entry.username, associated_data=b"username"),
            password=self._cipher.encrypt_text(entry.password, associated_data=b"password"),
            url=self._cipher.encrypt_text(entry.url, associated_data=b"url"),
            notes=self._cipher.encrypt_text(entry.notes, associated_data=b"notes"),
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )

    def _row_to_entry(self, row: dict) -> PasswordEntry:
        return PasswordEntry(
            entry_id=int(row["id"]),
            category=str(row["category"]),
            title=str(row["title"]),
            username=self._cipher.decrypt_text(str(row["username_enc"]), associated_data=b"username"),
            password=self._cipher.decrypt_text(str(row["password_enc"]), associated_data=b"password"),
            url=self._cipher.decrypt_text(str(row["url_enc"]), associated_data=b"url"),
            notes=self._cipher.decrypt_text(str(row["notes_enc"]), associated_data=b"notes"),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )
