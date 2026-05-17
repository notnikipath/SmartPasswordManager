from __future__ import annotations

import base64
import json
from dataclasses import dataclass

from core.config import AppConfig, SecurityConfig, ensure_runtime_dirs
from core.crypto.key_derivation import derive_key, generate_salt, hash_master_password, verify_master_password
from core.database.db_manager import DatabaseManager
from core.services.audit_service import AuditService


@dataclass(frozen=True)
class SessionContext:
    db_manager: DatabaseManager
    data_key: bytes
    security: SecurityConfig


class AuthService:
    def __init__(self, app_config: AppConfig, security: SecurityConfig, audit: AuditService) -> None:
        self._app_config = app_config
        self._security = security
        self._audit = audit
        ensure_runtime_dirs(app_config)

    def is_master_password_set(self) -> bool:
        return self._app_config.meta_path().exists()

    def create_master_password(self, master_password: str) -> None:
        if self.is_master_password_set():
            raise RuntimeError("Master password already initialized")

        salt = generate_salt(self._security.master_salt_bytes)
        master_hash = hash_master_password(master_password, salt, self._security.master_iterations)
        payload = {
            "salt_b64": base64.b64encode(salt).decode("ascii"),
            "hash_b64": master_hash,
            "iterations": self._security.master_iterations,
        }
        self._write_meta(payload)

        session = self.open_session(master_password)
        session.db_manager.initialize_schema()

    def open_session(self, master_password: str) -> SessionContext:
        meta = self._read_meta()
        salt = base64.b64decode(meta["salt_b64"].encode("ascii"))
        iterations = int(meta["iterations"])
        expected_hash = meta["hash_b64"]

        if not verify_master_password(master_password, salt, iterations, expected_hash):
            self._audit.log_login_failed()
            raise PermissionError("Invalid master password")

        db_key = derive_key(master_password, salt + b":db", iterations, length=self._security.aes_key_size)
        data_key = derive_key(master_password, salt + b":data", iterations, length=self._security.aes_key_size)

        manager = DatabaseManager(
            db_path=self._app_config.db_path(),
            db_key=db_key,
            kdf_iterations=self._security.sqlcipher_kdf_iter,
        )
        manager.initialize_schema()
        self._audit.log_login_success()
        return SessionContext(db_manager=manager, data_key=data_key, security=self._security)

    def _read_meta(self) -> dict[str, str | int]:
        meta_path = self._app_config.meta_path()
        if not meta_path.exists():
            raise FileNotFoundError("Master password metadata not found")
        with meta_path.open("r", encoding="utf-8") as meta_file:
            return json.load(meta_file)

    def _write_meta(self, payload: dict[str, str | int]) -> None:
        meta_path = self._app_config.meta_path()
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with meta_path.open("w", encoding="utf-8") as meta_file:
            json.dump(payload, meta_file, ensure_ascii=True, indent=2)
