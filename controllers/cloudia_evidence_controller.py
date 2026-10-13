"""Controller for generating monthly Cloudia evidence folders."""

from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox

from services.cloudia_evidence_service import CloudiaEvidenceServiceError
from services.kintone_service import KintoneServiceError


class _CloudiaEvidenceWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        service,
        records,
        month: int,
        year: int,
        request_pdf: str,
    ) -> None:
        super().__init__()
        self._service = service
        self._records = tuple(records)
        self._month = month
        self._year = year
        self._request_pdf = request_pdf

    def run(self) -> None:
        try:
            result = self._service.generate(
                self._records,
                self._month,
                self._year,
                self._request_pdf,
            )
        except (CloudiaEvidenceServiceError, KintoneServiceError) as error:
            self.failed.emit(str(error))
        except Exception:
            self.failed.emit(
                "An unexpected error occurred while generating Cloudia "
                "evidence."
            )
        else:
            self.succeeded.emit(result)


class CloudiaEvidenceController:
    """Coordinate evidence generation from matched spreadsheet records."""

    def __init__(self, view, service, spreadsheet_controller) -> None:
        self.view = view
        self.service = service
        self.spreadsheet_controller = spreadsheet_controller
        self._worker: _CloudiaEvidenceWorker | None = None

        self.view.generate_cloudia_evidence_clicked.connect(self.generate)

    def generate(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        records = self.spreadsheet_controller.spreadsheet_records
        if records is None:
            QMessageBox.warning(
                self.view,
                "Spreadsheet Not Ready",
                "Validate and reconcile the spreadsheet before generating "
                "Cloudia evidence.",
            )
            return

        month, year = self.view.statement_period()
        spreadsheet_path = self.spreadsheet_controller.spreadsheet_file_path
        initial_directory = (
            str(Path(spreadsheet_path).resolve().parent)
            if spreadsheet_path
            else str(Path.cwd())
        )
        request_pdf, _ = QFileDialog.getOpenFileName(
            self.view,
            "Select Kintone request PDF",
            initial_directory,
            "PDF Files (*.pdf)",
        )
        if not request_pdf:
            return

        self.view.set_cloudia_evidence_busy(True)
        self._worker = _CloudiaEvidenceWorker(
            self.service,
            records,
            month,
            year,
            request_pdf,
        )
        self._worker.succeeded.connect(self._generation_succeeded)
        self._worker.failed.connect(self._generation_failed)
        self._worker.finished.connect(self._worker_finished)
        self._worker.start()

    def _generation_succeeded(self, result) -> None:
        QMessageBox.information(
            self.view,
            "Cloudia Evidence Generated",
            f"Folder: {result.output_folder.name}\n"
            f"Evidence folders: {result.record_folder_count}\n"
            f"Request pages: {result.request_page_count}\n"
            f"Attachments: {result.attachment_count}",
        )

    def _generation_failed(self, message: str) -> None:
        QMessageBox.warning(
            self.view,
            "Unable to Generate Cloudia Evidence",
            message,
        )

    def _worker_finished(self) -> None:
        self.view.set_cloudia_evidence_busy(False)
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
