from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SecurityConfig:
    master_salt_bytes: int = 16
    master_iterations: int = 390_000
    sqlcipher_kdf_iter: int = 256_000
    aes_key_size: int = 32
    aes_nonce_size: int = 12


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "Smart Password Manager"
    data_dir_name: str = ".smart_password_manager"
    base_data_dir: str | None = None
    db_filename: str = "vault.db"
    meta_filename: str = "vault.meta.json"
    audit_filename: str = "audit.log"
    default_clipboard_clear_seconds: int = 15

    def data_dir(self) -> Path:
        if self.base_data_dir:
            return Path(self.base_data_dir)
        return Path.home() / self.data_dir_name

    def db_path(self) -> Path:
        return self.data_dir() / self.db_filename

    def meta_path(self) -> Path:
        return self.data_dir() / self.meta_filename

    def audit_log_path(self) -> Path:
        return self.data_dir() / self.audit_filename

    def export_dir(self) -> Path:
        return self.data_dir() / "exports"


def ensure_runtime_dirs(config: AppConfig) -> None:
    data_dir = config.data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    config.export_dir().mkdir(parents=True, exist_ok=True)
