from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path

from core.crypto.aes_gcm import AesGcmCipher
from core.crypto.key_derivation import derive_key, generate_salt
from core.models.password_entry import PasswordEntry
from core.services.audit_service import AuditService


class ExportService:
    def __init__(self, audit: AuditService) -> None:
        self._audit = audit

    def export_encrypted(self, entries: list[PasswordEntry], output_path: Path, export_password: str) -> Path:
        salt = generate_salt(16)
        iterations = 250_000
        export_key = derive_key(export_password, salt, iterations, length=32)
        cipher = AesGcmCipher(export_key)

        plain_payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "entries": [entry.__dict__ for entry in entries],
        }
        encrypted_payload = cipher.encrypt_text(json.dumps(plain_payload, ensure_ascii=False), associated_data=b"export")

        file_payload = {
            "version": 1,
            "salt_b64": base64.b64encode(salt).decode("ascii"),
            "iterations": iterations,
            "cipher": "AES-256-GCM",
            "payload": encrypted_payload,
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(file_payload, ensure_ascii=True, indent=2), encoding="utf-8")
        self._audit.log_export(str(output_path))
        return output_path
