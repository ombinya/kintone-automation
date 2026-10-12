"""Main application window and page-level UI behavior."""

from pathlib import Path

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMainWindow

from gen_ui.design_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    """Display the generated form without depending on the Designer file."""

    browse_statement_file_clicked = Signal()
    unlock_statement_file_clicked = Signal()
    browse_spreadsheet_file_clicked = Signal()
    validate_spreadsheet_file_clicked = Signal()
    reconcile_statement_spreadsheet_clicked = Signal()
    reconcile_spreadsheet_kintone_clicked = Signal()
    period_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._configure_statement_inputs()
        self._configure_spreadsheet_inputs()
        self._select_current_period()
        self._connect_navigation()
        self._connect_statement_actions()
        self._connect_spreadsheet_actions()
        self._connect_kintone_actions()
        self.set_statement_unlocked(False)
        self.set_spreadsheet_valid(False)
        self.set_reconciliation_complete(False)

    def _configure_statement_inputs(self) -> None:
        """Configure behavior that must survive UI regeneration."""
        file_display = self.ui.statement_file_name
        if isinstance(file_display, QLabel):
            self._statement_file_label = file_display
        else:
            layout = file_display.layout()
            if layout is None:
                layout = QHBoxLayout(file_display)
                layout.setContentsMargins(6, 0, 6, 0)

            self._statement_file_label = QLabel(file_display)
            self._statement_file_label.setWordWrap(True)
            layout.addWidget(self._statement_file_label)

        self.ui.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.ui.password_input.setPlaceholderText(
            "Enter statement password"
        )

    def _configure_spreadsheet_inputs(self) -> None:
        file_display = self.ui.spreadsheet_file_name
        if isinstance(file_display, QLabel):
            self._spreadsheet_file_label = file_display
        else:
            layout = file_display.layout()
            if layout is None:
                layout = QHBoxLayout(file_display)
                layout.setContentsMargins(6, 0, 6, 0)

            self._spreadsheet_file_label = QLabel(file_display)
            self._spreadsheet_file_label.setWordWrap(True)
            layout.addWidget(self._spreadsheet_file_label)

    def _select_current_period(self) -> None:
        today = QDate.currentDate()
        month_index = self.ui.month_input_combo.findText(
            today.toString("MMMM")
        )
        year_index = self.ui.year_input_combo.findText(str(today.year()))

        if month_index >= 0:
            self.ui.month_input_combo.setCurrentIndex(month_index)
        if year_index >= 0:
            self.ui.year_input_combo.setCurrentIndex(year_index)

    def _connect_navigation(self) -> None:
        page_for_button = {
            self.ui.to_spreadsheet_page_button:
                self.ui.spreadsheet_records_page,
            self.ui.to_kintone_page: self.ui.kintone_page,
            self.ui.back_to_statement_page: self.ui.mpesa_statement_page,
            self.ui.to_cloudia_evidence_page:
                self.ui.cloudia_evidence_page,
            self.ui.back_to_spreadsheet_page:
                self.ui.spreadsheet_records_page,
            self.ui.back_to_kintone_page: self.ui.kintone_page,
        }

        for button, page in page_for_button.items():
            button.clicked.connect(
                lambda checked=False, target=page:
                    self.ui.stackedWidget.setCurrentWidget(target)
            )

    def show_statement_page(self) -> None:
        self.ui.stackedWidget.setCurrentWidget(
            self.ui.mpesa_statement_page
        )

    def _connect_statement_actions(self) -> None:
        self.ui.browse_statement_file_button.clicked.connect(
            self.browse_statement_file_clicked
        )
        self.ui.unlock_file_button.clicked.connect(
            self.unlock_statement_file_clicked
        )
        self.ui.password_input.returnPressed.connect(
            self.unlock_statement_file_clicked
        )
        self.ui.month_input_combo.currentIndexChanged.connect(
            self.period_changed
        )
        self.ui.year_input_combo.currentIndexChanged.connect(
            self.period_changed
        )

    def _connect_spreadsheet_actions(self) -> None:
        self.ui.browse_spreadsheet_file_button.clicked.connect(
            self.browse_spreadsheet_file_clicked
        )
        self.ui.validate_file_button.clicked.connect(
            self.validate_spreadsheet_file_clicked
        )
        self.ui.reconcile_statement_spreadsheet_button.clicked.connect(
            self.reconcile_statement_spreadsheet_clicked
        )

    def _connect_kintone_actions(self) -> None:
        self.ui.reconcile_spreadsheet_kintone_button.clicked.connect(
            self.reconcile_spreadsheet_kintone_clicked
        )

    def set_statement_file_path(self, file_path: str) -> None:
        self._statement_file_label.setText(Path(file_path).name)
        self._statement_file_label.setToolTip(file_path)
        self.ui.statement_file_name.setToolTip(file_path)

    def statement_password(self) -> str:
        return self.ui.password_input.text()

    def statement_period(self) -> tuple[int, int]:
        return (
            self.ui.month_input_combo.currentIndex() + 1,
            int(self.ui.year_input_combo.currentText()),
        )

    def focus_statement_password(self) -> None:
        self.ui.password_input.setFocus()

    def clear_statement_password(self) -> None:
        self.ui.password_input.clear()

    def set_statement_unlocked(self, unlocked: bool) -> None:
        self.ui.to_spreadsheet_page_button.setEnabled(unlocked)
        self.set_reconciliation_complete(False)

    def set_statement_busy(self, busy: bool) -> None:
        self.ui.browse_statement_file_button.setEnabled(not busy)
        self.ui.password_input.setEnabled(not busy)
        self.ui.unlock_file_button.setEnabled(not busy)
        self.ui.unlock_file_button.setText(
            "Unlocking..." if busy else "Unlock File"
        )

    def set_spreadsheet_file_path(self, file_path: str) -> None:
        self._spreadsheet_file_label.setText(Path(file_path).name)
        self._spreadsheet_file_label.setToolTip(file_path)
        self.ui.spreadsheet_file_name.setToolTip(file_path)

    def set_spreadsheet_valid(self, valid: bool) -> None:
        self.ui.reconcile_statement_spreadsheet_button.setEnabled(valid)
        self.set_reconciliation_complete(False)

    def set_reconciliation_complete(self, complete: bool) -> None:
        self._reconciliation_complete = complete
        self.ui.to_kintone_page.setEnabled(complete)
        self.ui.reconcile_spreadsheet_kintone_button.setEnabled(complete)

    def set_kintone_busy(self, busy: bool) -> None:
        self.ui.reconcile_spreadsheet_kintone_button.setEnabled(
            not busy and getattr(self, "_reconciliation_complete", False)
        )
        self.ui.reconcile_spreadsheet_kintone_button.setText(
            "Reconciling..." if busy else "Reconcile"
        )
