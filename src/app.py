from __future__ import annotations

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from core.config import AppConfig, SecurityConfig
from core.services.audit_service import AuditService
from core.services.auth_service import AuthService
from core.services.export_service import ExportService
from core.services.password_service import PasswordService
from core.services.vulnerability_service import VulnerabilityService
from ui.windows.login_window import LoginWindow
from ui.windows.main_window import MainWindow
from utils.clipboard import ClipboardManager


def _load_stylesheet(app: QApplication) -> None:
    style_path = Path(__file__).resolve().parent / "ui" / "styles" / "theme.qss"
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))


def run() -> int:
    app = QApplication(sys.argv)
    _load_stylesheet(app)

    app_config = AppConfig(base_data_dir=os.environ.get("SPM_DATA_DIR"))
    security = SecurityConfig()
    audit = AuditService(app_config.audit_log_path())
    auth = AuthService(app_config, security, audit)

    login = LoginWindow(auth)
    if not login.exec():
        return 0
    if login.session is None:
        return 1

    session = login.session
    password_service = PasswordService(session.db_manager, session.data_key, audit)
    export_service = ExportService(audit)
    vulnerability_service = VulnerabilityService()
    clipboard = ClipboardManager(clear_after_seconds=app_config.default_clipboard_clear_seconds)

    window = MainWindow(
        app_config=app_config,
        password_service=password_service,
        export_service=export_service,
        vulnerability_service=vulnerability_service,
        clipboard=clipboard,
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
