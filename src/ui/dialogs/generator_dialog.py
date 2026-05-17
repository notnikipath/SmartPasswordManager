from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from utils.generators.password_generator import generate_password
from utils.validators.password_strength import estimate_password_strength


class GeneratorDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Генератор паролей")
        self.resize(420, 250)

        self._length = QSpinBox()
        self._length.setRange(8, 128)
        self._length.setValue(16)

        self._use_lower = QCheckBox("Строчные буквы")
        self._use_upper = QCheckBox("Заглавные буквы")
        self._use_digits = QCheckBox("Цифры")
        self._use_symbols = QCheckBox("Спецсимволы")
        self._use_lower.setChecked(True)
        self._use_upper.setChecked(True)
        self._use_digits.setChecked(True)
        self._use_symbols.setChecked(True)

        self._result = QLineEdit()
        self._result.setReadOnly(True)
        self._strength = QLabel("Сила: -")

        generate_button = QPushButton("Сгенерировать")
        use_button = QPushButton("Использовать")
        cancel_button = QPushButton("Отмена")

        generate_button.clicked.connect(self._on_generate)
        use_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        controls = QVBoxLayout()
        controls.addWidget(QLabel("Длина:"))
        controls.addWidget(self._length)
        controls.addWidget(self._use_lower)
        controls.addWidget(self._use_upper)
        controls.addWidget(self._use_digits)
        controls.addWidget(self._use_symbols)
        controls.addWidget(QLabel("Результат:"))
        controls.addWidget(self._result)
        controls.addWidget(self._strength)

        buttons = QHBoxLayout()
        buttons.addWidget(generate_button)
        buttons.addStretch(1)
        buttons.addWidget(use_button)
        buttons.addWidget(cancel_button)

        root = QVBoxLayout()
        root.addLayout(controls)
        root.addLayout(buttons)
        self.setLayout(root)

        self._on_generate()

    def generated_password(self) -> str:
        return self._result.text()

    def _on_generate(self) -> None:
        try:
            password = generate_password(
                length=self._length.value(),
                use_lowercase=self._use_lower.isChecked(),
                use_uppercase=self._use_upper.isChecked(),
                use_digits=self._use_digits.isChecked(),
                use_symbols=self._use_symbols.isChecked(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Ошибка генерации", str(exc))
            return

        self._result.setText(password)
        report = estimate_password_strength(password)
        self._strength.setText(f"Сила: {report.label}")
