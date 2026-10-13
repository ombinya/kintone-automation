"""Production entry point for the Accounting Management application.

This module uses the generated Python UI in ``gen_ui`` and never invokes
``pyside6-uic``. Regenerate the UI with ``python _main.py`` during development
and include ``gen_ui`` when packaging or deploying the application.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from controllers.kintone_controller import KintoneController
from controllers.cloudia_evidence_controller import CloudiaEvidenceController
from controllers.reconciliation_controller import ReconciliationController
from controllers.statement_controller import StatementController
from controllers.spreadsheet_controller import SpreadsheetController
from services.kintone_reconciliation_service import (
    KintoneReconciliationService,
)
from services.kintone_service import KintoneService
from services.cloudia_evidence_service import CloudiaEvidenceService
from services.reconciliation_service import ReconciliationService
from services.spreadsheet_service import SpreadsheetService
from services.statement_service import StatementService
from views.main_window import MainWindow


PROJECT_DIR = Path(__file__).resolve().parent


class Application:
    """Own the application's long-lived objects."""

    def __init__(self) -> None:
        self.statement_service = StatementService(PROJECT_DIR)
        self.spreadsheet_service = SpreadsheetService(PROJECT_DIR)
        self.reconciliation_service = ReconciliationService()
        self.kintone_service = KintoneService()
        self.cloudia_evidence_service = CloudiaEvidenceService(
            PROJECT_DIR,
            self.kintone_service,
        )
        self.kintone_reconciliation_service = (
            KintoneReconciliationService()
        )
        self.main_window = MainWindow()
        self.statement_controller = StatementController(
            self.main_window,
            self.statement_service,
        )
        self.spreadsheet_controller = SpreadsheetController(
            self.main_window,
            self.spreadsheet_service,
        )
        self.reconciliation_controller = ReconciliationController(
            self.main_window,
            self.reconciliation_service,
            self.spreadsheet_service,
            self.statement_controller,
            self.spreadsheet_controller,
        )
        self.kintone_controller = KintoneController(
            self.main_window,
            self.kintone_service,
            self.kintone_reconciliation_service,
            self.spreadsheet_service,
            self.spreadsheet_controller,
        )
        self.cloudia_evidence_controller = CloudiaEvidenceController(
            self.main_window,
            self.cloudia_evidence_service,
            self.spreadsheet_controller,
        )

    def start(self) -> None:
        self.main_window.show_statement_page()
        self.main_window.show()


def main() -> int:
    qt_application = QApplication(sys.argv)
    application = Application()
    application.start()
    return qt_application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
