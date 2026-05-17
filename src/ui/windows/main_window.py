from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.config import AppConfig
from core.models.password_entry import PasswordEntry
from core.services.export_service import ExportService
from core.services.password_service import DEFAULT_CATEGORIES, PasswordService
from core.services.vulnerability_service import VulnerabilityService
from ui.controls.strength_meter import StrengthMeter
from ui.dialogs.entry_dialog import EntryDialog
from ui.dialogs.generator_dialog import GeneratorDialog
from utils.clipboard import ClipboardManager


class MainWindow(QMainWindow):
    def __init__(
        self,
        app_config: AppConfig,
        password_service: PasswordService,
        export_service: ExportService,
        vulnerability_service: VulnerabilityService,
        clipboard: ClipboardManager,
    ) -> None:
        super().__init__()
        self._config = app_config
        self._password_service = password_service
        self._export_service = export_service
        self._vulnerability_service = vulnerability_service
        self._clipboard = clipboard

        self._entries: list[PasswordEntry] = []
        self._selected_entry_id: int | None = None

        self.setWindowTitle("Умный менеджер паролей")
        self.resize(1200, 760)

        self._create_toolbar()
        self._create_layout()
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Готово")
        self._refresh_entries()

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        add_action = QAction("Добавить", self)
        edit_action = QAction("Редактировать", self)
        delete_action = QAction("Удалить", self)
        generator_action = QAction("Генератор", self)
        export_action = QAction("Экспорт", self)
        analyze_action = QAction("Анализ уязвимостей", self)

        add_action.triggered.connect(self._on_add)
        edit_action.triggered.connect(self._on_edit)
        delete_action.triggered.connect(self._on_delete)
        generator_action.triggered.connect(self._on_open_generator)
        export_action.triggered.connect(self._on_export)
        analyze_action.triggered.connect(self._on_analyze)

        toolbar.addAction(add_action)
        toolbar.addAction(edit_action)
        toolbar.addAction(delete_action)
        toolbar.addSeparator()
        toolbar.addAction(generator_action)
        toolbar.addSeparator()
        toolbar.addAction(export_action)
        toolbar.addAction(analyze_action)
        toolbar.addSeparator()

        self._search = QLineEdit()
        self._search.setPlaceholderText("Поиск по названию...")
        self._search.textChanged.connect(self._refresh_entries)
        toolbar.addWidget(QLabel("Поиск: "))
        toolbar.addWidget(self._search)

    def _create_layout(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._category_list = QListWidget()
        self._category_list.addItems(["Все", *DEFAULT_CATEGORIES])
        self._category_list.setMaximumWidth(220)
        self._category_list.currentTextChanged.connect(self._refresh_entries)
        self._category_list.setCurrentRow(0)

        content_widget = QWidget()
        content_layout = QVBoxLayout()

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Название", "Логин", "Категория", "Обновлено"])
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.itemSelectionChanged.connect(self._on_table_selection_changed)

        self._title_view = QLineEdit()
        self._title_view.setReadOnly(True)
        self._category_view = QLineEdit()
        self._category_view.setReadOnly(True)
        self._username_view = QLineEdit()
        self._username_view.setReadOnly(True)
        self._password_view = QLineEdit()
        self._password_view.setReadOnly(True)
        self._password_view.setEchoMode(QLineEdit.EchoMode.Password)
        self._url_view = QLineEdit()
        self._url_view.setReadOnly(True)
        self._notes_view = QTextEdit()
        self._notes_view.setReadOnly(True)
        self._strength_meter = StrengthMeter()

        copy_login_btn = QPushButton("Копировать логин")
        copy_pass_btn = QPushButton("Копировать пароль")
        show_pass_btn = QPushButton("Показать/скрыть пароль")
        copy_login_btn.clicked.connect(self._copy_username)
        copy_pass_btn.clicked.connect(self._copy_password)
        show_pass_btn.clicked.connect(self._toggle_password_visibility)

        copy_layout = QHBoxLayout()
        copy_layout.addWidget(copy_login_btn)
        copy_layout.addWidget(copy_pass_btn)
        copy_layout.addWidget(show_pass_btn)
        copy_layout.addStretch(1)

        details = QFormLayout()
        details.addRow("Название:", self._title_view)
        details.addRow("Категория:", self._category_view)
        details.addRow("Логин:", self._username_view)
        details.addRow("Пароль:", self._password_view)
        details.addRow("", self._strength_meter)
        details.addRow("URL:", self._url_view)
        details.addRow("Заметки:", self._notes_view)

        content_layout.addWidget(self._table, 3)
        content_layout.addLayout(details, 2)
        content_layout.addLayout(copy_layout)
        content_widget.setLayout(content_layout)

        splitter.addWidget(self._category_list)
        splitter.addWidget(content_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root_layout = QVBoxLayout()
        root_layout.addWidget(splitter)
        root.setLayout(root_layout)

    def _refresh_entries(self) -> None:
        category = self._category_list.currentItem().text() if self._category_list.currentItem() else "Все"
        query = self._search.text().strip()
        self._entries = self._password_service.list_entries(category=category, query=query)

        self._table.setRowCount(len(self._entries))
        for row_idx, entry in enumerate(self._entries):
            self._table.setItem(row_idx, 0, QTableWidgetItem(entry.title))
            self._table.setItem(row_idx, 1, QTableWidgetItem(entry.username))
            self._table.setItem(row_idx, 2, QTableWidgetItem(entry.category))
            self._table.setItem(row_idx, 3, QTableWidgetItem(entry.updated_at or ""))
            if entry.entry_id is not None:
                self._table.item(row_idx, 0).setData(Qt.ItemDataRole.UserRole, entry.entry_id)

        if self._entries:
            self._table.selectRow(0)
        else:
            self._clear_details()

    def _on_table_selection_changed(self) -> None:
        items = self._table.selectedItems()
        if not items:
            self._clear_details()
            return

        row = items[0].row()
        entry = self._entries[row]
        self._selected_entry_id = entry.entry_id
        self._title_view.setText(entry.title)
        self._category_view.setText(entry.category)
        self._username_view.setText(entry.username)
        self._password_view.setText(entry.password)
        self._url_view.setText(entry.url)
        self._notes_view.setPlainText(entry.notes)
        self._strength_meter.update_strength(entry.password)

    def _on_add(self) -> None:
        dialog = EntryDialog(categories=list(DEFAULT_CATEGORIES), parent=self)
        if dialog.exec():
            entry = dialog.entry_data()
            if not entry.title or not entry.password:
                QMessageBox.warning(self, "Ошибка", "Название и пароль обязательны.")
                return
            self._password_service.create_entry(entry)
            self._refresh_entries()
            self.statusBar().showMessage("Запись добавлена", 3000)

    def _on_edit(self) -> None:
        entry = self._current_entry()
        if not entry:
            QMessageBox.information(self, "Информация", "Выберите запись для редактирования.")
            return
        dialog = EntryDialog(categories=list(DEFAULT_CATEGORIES), parent=self, entry=entry)
        if dialog.exec():
            updated = dialog.entry_data()
            if not updated.title or not updated.password:
                QMessageBox.warning(self, "Ошибка", "Название и пароль обязательны.")
                return
            if entry.entry_id is None:
                return
            self._password_service.update_entry(entry.entry_id, updated)
            self._refresh_entries()
            self.statusBar().showMessage("Запись обновлена", 3000)

    def _on_delete(self) -> None:
        entry = self._current_entry()
        if not entry or entry.entry_id is None:
            QMessageBox.information(self, "Информация", "Выберите запись для удаления.")
            return
        confirm = QMessageBox.question(
            self,
            "Удаление записи",
            f"Удалить запись '{entry.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._password_service.delete_entry(entry.entry_id)
            self._refresh_entries()
            self.statusBar().showMessage("Запись удалена", 3000)

    def _on_open_generator(self) -> None:
        dialog = GeneratorDialog(self)
        if dialog.exec():
            self._clipboard.copy_with_auto_clear(dialog.generated_password())
            self.statusBar().showMessage(
                "Сгенерированный пароль скопирован. Буфер будет очищен автоматически.",
                5000,
            )

    def _on_export(self) -> None:
        export_password, ok = QInputDialog.getText(
            self,
            "Пароль экспорта",
            "Введите пароль для шифрования файла экспорта:",
            QLineEdit.EchoMode.Password,
        )
        if not ok or not export_password:
            return

        default_name = datetime.now().strftime("vault_export_%Y%m%d_%H%M%S.spmx")
        default_path = str(self._config.export_dir() / default_name)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить экспорт",
            default_path,
            "Smart Password Manager Export (*.spmx)",
        )
        if not file_path:
            return

        try:
            exported = self._export_service.export_encrypted(
                entries=self._password_service.list_entries(),
                output_path=Path(file_path),
                export_password=export_password,
            )
            self.statusBar().showMessage(f"Экспорт сохранен: {exported}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка экспорта", str(exc))

    def _on_analyze(self) -> None:
        report = self._vulnerability_service.analyze(self._password_service.list_entries())
        weak_section = (
            "\n".join(f"- {item}" for item in report.weak_entries)
            if report.weak_entries
            else "Слабых паролей не обнаружено."
        )
        reused_section = (
            "\n".join(f"- {'; '.join(group)}" for group in report.reused_groups)
            if report.reused_groups
            else "Повторяющихся паролей не обнаружено."
        )
        QMessageBox.information(
            self,
            "Анализ уязвимостей",
            f"Слабые пароли:\n{weak_section}\n\nПовторяющиеся пароли:\n{reused_section}",
        )

    def _copy_username(self) -> None:
        entry = self._current_entry()
        if entry:
            self._clipboard.copy_with_auto_clear(entry.username)
            self.statusBar().showMessage("Логин скопирован. Буфер будет очищен автоматически.", 3000)

    def _copy_password(self) -> None:
        entry = self._current_entry()
        if entry:
            self._clipboard.copy_with_auto_clear(entry.password)
            self.statusBar().showMessage("Пароль скопирован. Буфер будет очищен автоматически.", 3000)

    def _toggle_password_visibility(self) -> None:
        if self._password_view.echoMode() == QLineEdit.EchoMode.Password:
            self._password_view.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self._password_view.setEchoMode(QLineEdit.EchoMode.Password)

    def _current_entry(self) -> PasswordEntry | None:
        if self._selected_entry_id is None:
            return None
        for entry in self._entries:
            if entry.entry_id == self._selected_entry_id:
                return entry
        return None

    def _clear_details(self) -> None:
        self._selected_entry_id = None
        self._title_view.clear()
        self._category_view.clear()
        self._username_view.clear()
        self._password_view.clear()
        self._url_view.clear()
        self._notes_view.clear()
        self._strength_meter.update_strength("")
