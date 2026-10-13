"""Controller for selecting and validating M-Pesa record spreadsheets."""

from calendar import month_name
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from services.spreadsheet_service import SpreadsheetServiceError


PROJECT_DIR = Path(__file__).resolve().parent.parent


class SpreadsheetController:
    """Coordinate the spreadsheet-records page and its validation."""

    def __init__(self, view, spreadsheet_service) -> None:
        self.view = view
        self.spreadsheet_service = spreadsheet_service
        self.spreadsheet_file_path: str | None = None
        self.validated_spreadsheet_path: str | None = None
        self.spreadsheet_records: list[dict] | None = None
        self.spreadsheet_worksheet_name: str | None = None

        self.view.browse_spreadsheet_file_clicked.connect(
            self.choose_spreadsheet_file
        )
        self.view.validate_spreadsheet_file_clicked.connect(
            self.validate_spreadsheet_file
        )
        self.view.period_changed.connect(self.invalidate_validation)

    def choose_spreadsheet_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Select M-Pesa records spreadsheet",
            str(PROJECT_DIR),
            "Excel Workbooks (*.xlsx)",
        )
        if not file_path:
            return

        self.spreadsheet_file_path = file_path
        self.invalidate_validation()
        self.view.set_spreadsheet_file_path(file_path)

    def validate_spreadsheet_file(self) -> None:
        month, year = self.view.statement_period()
        try:
            result = self.spreadsheet_service.validate_file(
                self.spreadsheet_file_path or "",
                month,
                year,
            )
        except SpreadsheetServiceError as error:
            self.invalidate_validation()
            QMessageBox.warning(
                self.view,
                "Invalid Spreadsheet",
                str(error),
            )
            return

        self.validated_spreadsheet_path = str(result.file_path)
        self.spreadsheet_records = list(result.records)
        self.spreadsheet_worksheet_name = result.worksheet_name
        self.view.set_spreadsheet_records(self.spreadsheet_records)
        self.view.set_spreadsheet_valid(True)
        message = (
            f"The spreadsheet is valid for {month_name[month]} {year}.\n\n"
            f"Records captured: {len(result.records)}"
        )
        if result.records:
            message += (
                f"\n\nFirst {min(5, len(result.records))} records:\n"
                f"{self._format_record_preview(result.records)}"
            )
        QMessageBox.information(
            self.view,
            "Spreadsheet Validated",
            message,
        )

    @staticmethod
    def _format_record_preview(records) -> str:
        preview_lines = []
        for index, record in enumerate(records[:5], start=1):
            record_date = record.get("Date")
            if hasattr(record_date, "date"):
                date_text = record_date.date().isoformat()
            else:
                date_text = str(record_date)[:10]

            preview_lines.append(
                f"{index}. {date_text} | "
                f"Code: {record.get('Transaction Code')} | "
                f"Kintone ID: {record.get('Kintone Record ID')} | "
                f"Account: {record.get('Account Code')} | "
                f"Amount: {record.get('Amount')} | "
                f"Charge: {record.get('Trans Chr.')}"
            )

        return "\n".join(preview_lines)

    def invalidate_validation(self) -> None:
        self.validated_spreadsheet_path = None
        self.spreadsheet_records = None
        self.spreadsheet_worksheet_name = None
        self.view.set_spreadsheet_records(())
        self.view.set_spreadsheet_valid(False)
