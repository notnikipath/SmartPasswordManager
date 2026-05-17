from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from core.services.auth_service import AuthService, SessionContext


class LoginWindow(QDialog):
    def __init__(self, auth_service: AuthService) -> None:
        super().__init__()
        self._auth = auth_service
        self.session: SessionContext | None = None

        self._setup_mode = not self._auth.is_master_password_set()
        self.setWindowTitle("Мастер-пароль")
        self.setFixedSize(420, 220)

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

        submit = QPushButton("Войти" if not self._setup_mode else "Создать хранилище")
        submit.clicked.connect(self._on_submit)

        root = QVBoxLayout()
        root.addWidget(self._description)
        root.addLayout(form)
        root.addWidget(submit)
        self.setLayout(root)

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
