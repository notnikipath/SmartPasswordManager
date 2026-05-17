from __future__ import annotations

from pathlib import Path

from core.config import AppConfig, SecurityConfig
from core.models.password_entry import PasswordEntry
from core.services.audit_service import AuditService
from core.services.auth_service import AuthService
from core.services.password_service import PasswordService


def test_password_service_crud(tmp_path: Path) -> None:
    app_config = AppConfig(base_data_dir=str(tmp_path))
    security = SecurityConfig(master_iterations=20_000, sqlcipher_kdf_iter=20_000)
    audit = AuditService(app_config.audit_log_path())
    auth = AuthService(app_config, security, audit)

    auth.create_master_password("master-123")
    session = auth.open_session("master-123")
    service = PasswordService(session.db_manager, session.data_key, audit)

    created_id = service.create_entry(
        PasswordEntry(
            entry_id=None,
            category="Работа",
            title="GitHub",
            username="dev_user",
            password="Str0ng!Pass123",
            url="https://github.com",
            notes="2FA enabled",
        )
    )
    assert created_id > 0

    entries = service.list_entries()
    assert len(entries) == 1
    assert entries[0].title == "GitHub"

    service.update_entry(
        created_id,
        PasswordEntry(
            entry_id=created_id,
            category="Работа",
            title="GitHub Updated",
            username="dev_user",
            password="EvenStr0nger!Pass123",
            url="https://github.com",
            notes="updated",
        ),
    )
    updated = service.get_entry(created_id)
    assert updated is not None
    assert updated.title == "GitHub Updated"

    service.delete_entry(created_id)
    assert service.list_entries() == []
