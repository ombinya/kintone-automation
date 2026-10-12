"""Controller for selecting and unlocking an M-Pesa statement."""

from calendar import month_name
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox

from services.statement_service import StatementServiceError


PROJECT_DIR = Path(__file__).resolve().parent.parent
PDF_START_DIRECTORY = PROJECT_DIR


class _StatementUnlockWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        service,
        file_path: str,
        password: str,
        month: int,
        year: int,
    ) -> None:
        super().__init__()
        self._service = service
        self._file_path = file_path
        self._password = password
        self._month = month
        self._year = year

    def run(self) -> None:
        try:
            output = self._service.unlock_statement(
                self._file_path,
                self._password,
                self._month,
                self._year,
            )
        except StatementServiceError as error:
            self.failed.emit(str(error))
        except Exception:
            self.failed.emit(
                "An unexpected error occurred while unlocking the statement."
            )
        else:
            self.succeeded.emit(output)
        finally:
            self._password = ""


class StatementController:
    """Coordinate the statement page, file dialog, and conversion service."""

    def __init__(self, view, statement_service) -> None:
        self.view = view
        self.statement_service = statement_service
        self.statement_file_path: str | None = None
        self.statement_workbook_path: str | None = None
        self.statement_transactions: list[dict] | None = None
        self._worker: _StatementUnlockWorker | None = None

        self.view.browse_statement_file_clicked.connect(
            self.choose_statement_file
        )
        self.view.unlock_statement_file_clicked.connect(
            self.unlock_statement_file
        )
        self.view.period_changed.connect(self.invalidate_validation)

    def choose_statement_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Select M-Pesa statement",
            str(PDF_START_DIRECTORY),
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        self.statement_file_path = file_path
        self.statement_workbook_path = None
        self.statement_transactions = None
        self.view.set_statement_file_path(file_path)
        self.view.set_statement_unlocked(False)

    def unlock_statement_file(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return

        if not self.statement_file_path:
            QMessageBox.warning(
                self.view,
                "Statement Required",
                "Select an M-Pesa statement PDF first.",
            )
            return

        password = self.view.statement_password()
        if not password:
            QMessageBox.warning(
                self.view,
                "Password Required",
                "Enter the statement password.",
            )
            self.view.focus_statement_password()
            return

        self.statement_workbook_path = None
        self.statement_transactions = None
        self.view.set_statement_unlocked(False)
        self.view.set_statement_busy(True)
        month, year = self.view.statement_period()

        self._worker = _StatementUnlockWorker(
            self.statement_service,
            self.statement_file_path,
            password,
            month,
            year,
        )
        self._worker.succeeded.connect(self._unlock_succeeded)
        self._worker.failed.connect(self._unlock_failed)
        self._worker.finished.connect(self._worker_finished)
        self._worker.start()

    def _unlock_succeeded(self, result) -> None:
        self.statement_workbook_path = str(result.workbook_path)
        self.statement_transactions = list(result.transactions)
        self.view.clear_statement_password()
        self.view.set_statement_unlocked(True)
        transaction_preview = self._format_transaction_preview(
            result.transactions
        )
        QMessageBox.information(
            self.view,
            "Statement Unlocked",
            f"The statement was unlocked and validated successfully.\n\n"
            f"Period: {month_name[result.month]} {result.year}\n"
            f"Transactions captured: {len(result.transactions)}\n\n"
            f"First {min(5, len(result.transactions))} transactions:\n"
            f"{transaction_preview}",
        )

    @staticmethod
    def _format_transaction_preview(transactions) -> str:
        preview_lines = []
        for index, transaction in enumerate(transactions[:5], start=1):
            completion_time = transaction.get("Completion Time")
            if hasattr(completion_time, "date"):
                transaction_date = completion_time.date().isoformat()
            else:
                transaction_date = str(completion_time)[:10]

            if transaction.get("Paid In") is not None:
                amount = f"Paid In: {transaction['Paid In']}"
            else:
                amount = f"Withdrawn: {transaction.get('Withdrawn')}"

            preview_lines.append(
                f"{index}. {transaction.get('Receipt No.')} | "
                f"{transaction_date} | {amount} | "
                f"Charge: {transaction.get('Transaction charge')} | "
                f"Payee: {transaction.get('Payee')}"
            )

        return "\n".join(preview_lines)

    def _unlock_failed(self, message: str) -> None:
        self.view.clear_statement_password()
        self.statement_transactions = None
        self.view.set_statement_unlocked(False)
        QMessageBox.warning(self.view, "Unable to Unlock Statement", message)

    def _worker_finished(self) -> None:
        self.view.set_statement_busy(False)
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None

    def invalidate_validation(self) -> None:
        self.statement_workbook_path = None
        self.statement_transactions = None
        self.view.set_statement_unlocked(False)
