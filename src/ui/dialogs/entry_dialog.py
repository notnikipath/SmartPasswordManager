from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from core.models.password_entry import PasswordEntry
from ui.controls.strength_meter import StrengthMeter


class EntryDialog(QDialog):
    def __init__(
        self,
        categories: list[str],
        parent=None,
        entry: PasswordEntry | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Запись пароля")
        self.resize(520, 420)

        self._category = QComboBox()
        self._category.addItems(categories)
        self._title = QLineEdit()
        self._username = QLineEdit()
        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._url = QLineEdit()
        self._notes = QTextEdit()
        self._strength = StrengthMeter()

        self._password.textChanged.connect(self._strength.update_strength)

        form = QFormLayout()
        form.addRow("Категория:", self._category)
        form.addRow("Название:", self._title)
        form.addRow("Логин:", self._username)
        form.addRow("Пароль:", self._password)
        form.addRow("", self._strength)
        form.addRow("URL:", self._url)
        form.addRow("Заметки:", self._notes)

        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)

        root = QVBoxLayout()
        root.addLayout(form)
        root.addLayout(buttons)
        self.setLayout(root)

        self._entry_id: int | None = None
        if entry:
            self._entry_id = entry.entry_id
            self._category.setCurrentText(entry.category)
            self._title.setText(entry.title)
            self._username.setText(entry.username)
            self._password.setText(entry.password)
            self._url.setText(entry.url)
            self._notes.setPlainText(entry.notes)
            self._strength.update_strength(entry.password)

    def entry_data(self) -> PasswordEntry:
        return PasswordEntry(
            entry_id=self._entry_id,
            category=self._category.currentText().strip(),
            title=self._title.text().strip(),
            username=self._username.text().strip(),
            password=self._password.text(),
            url=self._url.text().strip(),
            notes=self._notes.toPlainText().strip(),
        )
