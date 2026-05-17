from __future__ import annotations

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication


class ClipboardManager:
    def __init__(self, clear_after_seconds: int = 15) -> None:
        self._clear_after_ms = max(1, clear_after_seconds) * 1000
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.clear)

    def copy_with_auto_clear(self, value: str) -> None:
        clipboard = QApplication.clipboard()
        clipboard.setText(value)
        self._timer.start(self._clear_after_ms)

    def clear(self) -> None:
        QApplication.clipboard().clear()
