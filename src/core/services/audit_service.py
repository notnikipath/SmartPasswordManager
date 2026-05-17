from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class AuditService:
    def __init__(self, log_path: Path) -> None:
        self._logger = logging.getLogger("smart_password_manager.audit")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        if not self._logger.handlers:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def log_login_success(self) -> None:
        self._logger.info("LOGIN_SUCCESS")

    def log_login_failed(self) -> None:
        self._logger.warning("LOGIN_FAILED")

    def log_record_action(self, action: str, entry_id: int | None = None) -> None:
        self._logger.info("ENTRY_%s id=%s", action.upper(), entry_id)

    def log_export(self, filename: str) -> None:
        self._logger.info("EXPORT_CREATED file=%s", filename)
