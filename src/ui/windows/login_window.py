from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from core.database.db_manager import SQLCIPHER_AVAILABLE
from core.services.auth_service import AuthService, SessionContext


class LoginWindow(QDialog):
    def __init__(self, auth_service: AuthService) -> None:
        super().__init__()
        self._auth = auth_service
        self.session: SessionContext | None = None

        self._setup_mode = not self._auth.is_master_password_set()
        self.setWindowTitle("Мастер-пароль")
        self.setMinimumSize(500, 340)

        self._description = QLabel(
            "Первый запуск: создайте мастер-пароль."
            if self._setup_mode
            else "Введите мастер-пароль для входа."
        )
        self._description.setWordWrap(True)

        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm = QLineEdit()
        self._confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm.setVisible(self._setup_mode)

        form = QFormLayout()
        form.addRow("Мастер-пароль:", self._password)
        if self._setup_mode:
            form.addRow("Подтверждение:", self._confirm)

        visibility = QCheckBox("Показать пароль")
        visibility.toggled.connect(self._toggle_password_visibility)
        self._password.setAccessibleName("Мастер-пароль")
        self._confirm.setAccessibleName("Подтверждение мастер-пароля")
        self._password.returnPressed.connect(self._on_submit)
        self._confirm.returnPressed.connect(self._on_submit)

        submit = QPushButton("Войти" if not self._setup_mode else "Создать хранилище")
        submit.clicked.connect(self._on_submit)

        root = QVBoxLayout()
        root.addWidget(self._description)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)
        root.addLayout(form)
        root.addWidget(visibility)
        if not SQLCIPHER_AVAILABLE:
            notice = QLabel(
                "SQLCipher недоступен. Поля паролей защищены AES, "
                "но файл базы и названия записей не зашифрованы."
            )
            notice.setWordWrap(True)
            root.addWidget(notice)
        root.addWidget(submit)
        self.setLayout(root)

    def _toggle_password_visibility(self, visible: bool) -> None:
        mode = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self._password.setEchoMode(mode)
        self._confirm.setEchoMode(mode)

    def _on_submit(self) -> None:
        master_password = self._password.text()
        try:
            if self._setup_mode:
                confirm = self._confirm.text()
                if len(master_password) < 8:
                    QMessageBox.warning(self, "Ошибка", "Мастер-пароль должен быть не короче 8 символов.")
                    return
                if master_password != confirm:
                    QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
                    return
                self._auth.create_master_password(master_password)

            self.session = self._auth.open_session(master_password)
            self._password.clear()
            self._confirm.clear()
            self.accept()
        except PermissionError:
            QMessageBox.warning(self, "Ошибка", "Неверный мастер-пароль.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть хранилище: {exc}")
