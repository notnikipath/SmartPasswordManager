from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from utils.validators.password_strength import estimate_password_strength


class StrengthMeter(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label = QLabel("Сила пароля: -")
        self._progress = QProgressBar()
        self._progress.setRange(0, 7)
        self._progress.setValue(0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        layout.addWidget(self._progress)
        self.setLayout(layout)

    def update_strength(self, password: str) -> None:
        report = estimate_password_strength(password)
        self._label.setText(f"Сила пароля: {report.label}")
        self._progress.setValue(report.score)
        self._progress.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {report.color}; }}"
        )
