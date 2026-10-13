"""Controller for spreadsheet-to-Kintone reconciliation."""

from pathlib import Path
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog, QGridLayout, QMessageBox

from services.kintone_service import KintoneServiceError
from services.spreadsheet_service import SpreadsheetServiceError
from readers.mpesa_record_reader import MpesaRecordReader
from views.kintone_candidate_dialog import KintoneCandidateDialog


class _KintoneCandidatesWorker(QThread):
    succeeded = Signal(object, object)
    failed = Signal(str)

    def __init__(
        self,
        kintone_service,
        spreadsheet_rows,
        amount,
        payment_method: str,
    ) -> None:
        super().__init__()
        self._kintone_service = kintone_service
        self._spreadsheet_rows = tuple(spreadsheet_rows)
        self._amount = amount
        self._payment_method = payment_method

    def run(self) -> None:
        try:
            records = self._kintone_service.get_records_matching_amount(
                self._amount,
                self._payment_method,
            )
        except KintoneServiceError as error:
            self.failed.emit(str(error))
        except Exception:
            self.failed.emit(
                "An unexpected error occurred while finding Kintone records."
            )
        else:
            self.succeeded.emit(self._spreadsheet_rows, records)


class _KintoneReconciliationWorker(QThread):
    succeeded = Signal(object, object)
    failed = Signal(str)

    def __init__(
        self,
        kintone_service,
        reconciliation_service,
        spreadsheet_records,
        month: int,
        year: int,
        payment_method: str,
    ) -> None:
        super().__init__()
        self._kintone_service = kintone_service
        self._reconciliation_service = reconciliation_service
        self._spreadsheet_records = spreadsheet_records
        self._month = month
        self._year = year
        self._payment_method = payment_method

    def run(self) -> None:
        try:
            kintone_records = self._kintone_service.get_records_for_period(
                self._month,
                self._year,
                self._payment_method,
            )
            result = self._reconciliation_service.reconcile(
                self._spreadsheet_records,
                kintone_records,
                self._month,
                self._year,
                self._payment_method,
            )
            if result.unmatched_spreadsheet_records:
                outside_records = (
                    self._kintone_service.get_records_outside_period(
                        self._month,
                        self._year,
                        self._payment_method,
                    )
                )
                result = self._reconciliation_service.reconcile(
                    self._spreadsheet_records,
                    kintone_records,
                    self._month,
                    self._year,
                    self._payment_method,
                    outside_kintone_records=outside_records,
                    allow_incomplete_fallback=True,
                )
        except KintoneServiceError as error:
            self.failed.emit(str(error))
        except Exception:
            self.failed.emit(
                "An unexpected error occurred while reconciling Kintone "
                "records."
            )
        else:
            self.succeeded.emit(kintone_records, result)


class KintoneController:
    """Coordinate Kintone download and reconciliation from the Kintone page."""

    PAYMENT_METHODS = {
        "M-PESA1": "MPESA 1",
        "M-PESA2": "MPESA 2",
    }

    def __init__(
        self,
        view,
        kintone_service,
        reconciliation_service,
        spreadsheet_service,
        spreadsheet_controller,
    ) -> None:
        self.view = view
        self.kintone_service = kintone_service
        self.reconciliation_service = reconciliation_service
        self.spreadsheet_service = spreadsheet_service
        self.spreadsheet_controller = spreadsheet_controller
        self.kintone_records: list[dict] | None = None
        self.result = None
        self._worker: _KintoneReconciliationWorker | None = None
        self._candidate_worker: _KintoneCandidatesWorker | None = None

        self.view.spreadsheet_records_activated.connect(
            self.show_candidates_for_rows
        )
        self.view.reconcile_spreadsheet_kintone_clicked.connect(
            self.reconcile
        )
        self.view.period_changed.connect(self.invalidate_result)

    def show_candidates_for_rows(self, rows) -> None:
        if (
            self._candidate_worker is not None
            and self._candidate_worker.isRunning()
        ):
            return

        records = self.spreadsheet_controller.spreadsheet_records
        selected_rows = tuple(sorted(set(rows)))
        if (
            records is None
            or not selected_rows
            or any(row < 0 or row >= len(records) for row in selected_rows)
        ):
            return
        spreadsheet_records = tuple(records[row] for row in selected_rows)
        validation_error = self._selected_group_error(spreadsheet_records)
        if validation_error:
            QMessageBox.warning(
                self.view,
                "Invalid Spreadsheet Selection",
                validation_error,
            )
            return

        try:
            combined_amount = sum(
                (
                    Decimal(str(record.get("Amount")).replace(",", ""))
                    for record in spreadsheet_records
                ),
                Decimal("0"),
            )
        except (InvalidOperation, ValueError):
            QMessageBox.warning(
                self.view,
                "Invalid Spreadsheet Amount",
                "Every selected spreadsheet record must have a valid amount.",
            )
            return

        payment_method = self.PAYMENT_METHODS.get(
            self.spreadsheet_controller.spreadsheet_worksheet_name
        )
        if payment_method is None:
            QMessageBox.warning(
                self.view,
                "Unsupported Spreadsheet",
                "The validated spreadsheet must use the M-PESA1 or M-PESA2 "
                "worksheet before selecting a Kintone record.",
            )
            return

        self.view.set_kintone_candidate_lookup_busy(True)
        self._candidate_worker = _KintoneCandidatesWorker(
            self.kintone_service,
            selected_rows,
            combined_amount,
            payment_method,
        )
        self._candidate_worker.succeeded.connect(
            self._candidate_lookup_succeeded
        )
        self._candidate_worker.failed.connect(self._candidate_lookup_failed)
        self._candidate_worker.finished.connect(
            self._candidate_worker_finished
        )
        self._candidate_worker.start()

    def _candidate_lookup_succeeded(self, rows, candidates) -> None:
        spreadsheet_records = (
            self.spreadsheet_controller.spreadsheet_records or []
        )
        selected_rows = tuple(rows)
        if any(
            row < 0 or row >= len(spreadsheet_records)
            for row in selected_rows
        ):
            return

        used_ids = {
            str(record_id).strip()
            for index, record in enumerate(spreadsheet_records)
            if index not in selected_rows
            for record_id in (record.get("Kintone Record ID"),)
            if record_id not in (None, "")
        }
        available_candidates = [
            record
            for record in candidates
            if self.reconciliation_service.record_id(record) not in used_ids
        ]
        if not available_candidates:
            QMessageBox.information(
                self.view,
                "No Kintone Candidates",
                "No unused Kintone records with the same amount and payment "
                "method were found.",
            )
            return

        selected_records = tuple(
            spreadsheet_records[row] for row in selected_rows
        )
        dialog = KintoneCandidateDialog(
            selected_records,
            available_candidates,
            self.view,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if dialog.selected_record is not None:
            self._save_manual_selection(
                selected_records,
                dialog.selected_record,
            )

    def _save_manual_selection(
        self,
        spreadsheet_records,
        kintone_record,
    ) -> None:
        record_id = self.reconciliation_service.record_id(kintone_record)
        try:
            updated_copy = self.spreadsheet_service.save_kintone_ids_copy(
                self.spreadsheet_controller.spreadsheet_file_path,
                self.spreadsheet_controller.spreadsheet_records or [],
                tuple(
                    (spreadsheet_record, record_id)
                    for spreadsheet_record in spreadsheet_records
                ),
                allow_replacement=True,
            )
            month, year = self.view.statement_period()
            updated_result = self.spreadsheet_service.validate_file(
                str(updated_copy),
                month,
                year,
            )
        except SpreadsheetServiceError as error:
            QMessageBox.warning(
                self.view,
                "Unable to Save Kintone Record ID",
                str(error),
            )
            return

        updated_path = str(updated_copy)
        self.spreadsheet_controller.spreadsheet_file_path = updated_path
        self.spreadsheet_controller.validated_spreadsheet_path = updated_path
        self.spreadsheet_controller.spreadsheet_records = list(
            updated_result.records
        )
        self.spreadsheet_controller.spreadsheet_worksheet_name = (
            updated_result.worksheet_name
        )
        self.view.set_spreadsheet_file_path(updated_path)
        self.view.set_spreadsheet_records(
            self.spreadsheet_controller.spreadsheet_records
        )
        QMessageBox.information(
            self.view,
            "Kintone Record Selected",
            f"Kintone record {record_id} has been linked to "
            f"{len(spreadsheet_records)} spreadsheet record(s).",
        )

    @staticmethod
    def _selected_group_error(records) -> str | None:
        if len(records) == 1:
            return None

        row_numbers = []
        for record in records:
            try:
                row_numbers.append(
                    int(record.get(MpesaRecordReader.ROW_NUMBER_KEY))
                )
            except (TypeError, ValueError):
                return "The selected rows could not be mapped to the workbook."
        if row_numbers != list(
            range(row_numbers[0], row_numbers[0] + len(row_numbers))
        ):
            return "Select only consecutive spreadsheet rows."

        worksheet_names = {
            record.get(MpesaRecordReader.WORKSHEET_KEY) for record in records
        }
        if len(worksheet_names) != 1:
            return "All selected records must belong to the same worksheet."

        dates = {
            str(record.get("Date"))[:10]
            for record in records
        }
        if len(dates) != 1:
            return "Combined spreadsheet records must have the same date."

        payees = {
            " ".join(
                str(record.get("Payee/Payer") or "").casefold().split()
            )
            for record in records
        }
        if len(payees) != 1 or not next(iter(payees)):
            return "Combined spreadsheet records must have the same payee."
        return None

    def _candidate_lookup_failed(self, message: str) -> None:
        QMessageBox.warning(
            self.view,
            "Unable to Find Kintone Records",
            message,
        )

    def _candidate_worker_finished(self) -> None:
        self.view.set_kintone_candidate_lookup_busy(False)
        if self._candidate_worker is not None:
            self._candidate_worker.deleteLater()
            self._candidate_worker = None

    def reconcile(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return

        spreadsheet_records = self.spreadsheet_controller.spreadsheet_records
        if spreadsheet_records is None:
            QMessageBox.warning(
                self.view,
                "Spreadsheet Not Ready",
                "Validate and reconcile the spreadsheet with the statement "
                "before reconciling it with Kintone.",
            )
            return

        worksheet_name = (
            self.spreadsheet_controller.spreadsheet_worksheet_name
        )
        payment_method = self.PAYMENT_METHODS.get(worksheet_name)
        if payment_method is None:
            QMessageBox.warning(
                self.view,
                "Unsupported Spreadsheet",
                "The validated spreadsheet must use the M-PESA1 or M-PESA2 "
                "worksheet before it can be reconciled with Kintone.",
            )
            return

        month, year = self.view.statement_period()
        self.result = None
        self.kintone_records = None
        self.view.set_kintone_busy(True)
        self._worker = _KintoneReconciliationWorker(
            self.kintone_service,
            self.reconciliation_service,
            tuple(spreadsheet_records),
            month,
            year,
            payment_method,
        )
        self._worker.succeeded.connect(self._reconciliation_succeeded)
        self._worker.failed.connect(self._reconciliation_failed)
        self._worker.finished.connect(self._worker_finished)
        self._worker.start()

    def _reconciliation_succeeded(self, kintone_records, result) -> None:
        self.kintone_records = list(kintone_records)
        self.result = result
        updated_copy = None
        if result.matched_pairs:
            kintone_id_assignments = []
            for pair in result.matched_pairs:
                record_id = self.reconciliation_service.record_id(
                    pair.kintone_record
                )
                kintone_id_assignments.extend(
                    (spreadsheet_record, record_id)
                    for spreadsheet_record in pair.spreadsheet_records
                )

            try:
                updated_copy = self.spreadsheet_service.save_kintone_ids_copy(
                    self.spreadsheet_controller.spreadsheet_file_path,
                    self.spreadsheet_controller.spreadsheet_records or [],
                    kintone_id_assignments,
                )
                month, year = self.view.statement_period()
                updated_result = self.spreadsheet_service.validate_file(
                    str(updated_copy),
                    month,
                    year,
                )
            except SpreadsheetServiceError as error:
                self.result = None
                QMessageBox.warning(
                    self.view,
                    "Unable to Save Kintone Record IDs",
                    str(error),
                )
                return

            updated_path = str(updated_copy)
            self.spreadsheet_controller.spreadsheet_file_path = updated_path
            self.spreadsheet_controller.validated_spreadsheet_path = (
                updated_path
            )
            self.spreadsheet_controller.spreadsheet_records = list(
                updated_result.records
            )
            self.spreadsheet_controller.spreadsheet_worksheet_name = (
                updated_result.worksheet_name
            )
            self.view.set_spreadsheet_file_path(updated_path)
            self.view.set_spreadsheet_records(
                self.spreadsheet_controller.spreadsheet_records
            )

        eligible_count = (
            len(kintone_records)
            - len(result.excluded_old_kintone_records)
            - len(result.excluded_late_kintone_records)
            - len(result.excluded_payment_method_records)
            - len(result.excluded_incomplete_kintone_records)
        )
        payment_method = self.PAYMENT_METHODS.get(
            self.spreadsheet_controller.spreadsheet_worksheet_name,
            "",
        )
        matched_spreadsheet_rows = sum(
            len(pair.spreadsheet_records)
            for pair in result.matched_pairs
        )
        combined_groups = sum(
            len(pair.spreadsheet_records) > 1
            for pair in result.matched_pairs
        )

        message_box = QMessageBox(self.view)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("Kintone Reconciliation Complete")
        message_box.setText(
            "The spreadsheet and Kintone records have been checked."
        )
        message_box.setInformativeText(
            f"Spreadsheet records: "
            f"{len(self.spreadsheet_controller.spreadsheet_records or [])}\n"
            f"Payment method: {payment_method}\n"
            f"Eligible Kintone records: {eligible_count}\n"
            f"Matched Kintone records: {len(result.matched_pairs)}\n"
            f"Matched spreadsheet rows: {matched_spreadsheet_rows}\n"
            f"Combined spreadsheet groups: {combined_groups}\n"
            "Non-Completed fallback matches: "
            f"{len(result.noncompleted_fallback_matches)}\n"
            "Unique amount-only matches: "
            f"{len(result.amount_only_fallback_matches)}\n"
            "Ignored negative spreadsheet records: "
            f"{len(result.ignored_negative_spreadsheet_records)}\n"
            "Unmatched spreadsheet records: "
            f"{len(result.unmatched_spreadsheet_records)}\n"
            "Unmatched Kintone records: "
            f"{len(result.unmatched_kintone_records)}"
            + (
                f"\nUpdated spreadsheet: {Path(updated_copy).name}"
                if updated_copy is not None
                else ""
            )
        )
        details = self._format_result_details(result)
        if details:
            message_box.setDetailedText(details)
        message_box.setMinimumWidth(800)
        layout = message_box.layout()
        if isinstance(layout, QGridLayout):
            layout.setColumnMinimumWidth(1, 650)
        message_box.exec()

    def _reconciliation_failed(self, message: str) -> None:
        self.result = None
        self.kintone_records = None
        QMessageBox.warning(
            self.view,
            "Unable to Reconcile Kintone",
            message,
        )

    def _worker_finished(self) -> None:
        self.view.set_kintone_busy(False)
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None

    def invalidate_result(self) -> None:
        self.result = None
        self.kintone_records = None

    @classmethod
    def _format_result_details(cls, result) -> str:
        sections = []
        if result.matched_pairs:
            lines = ["MATCHED RECORDS"]
            for index, pair in enumerate(result.matched_pairs, start=1):
                if len(pair.spreadsheet_records) == 1:
                    spreadsheet_summary = cls._spreadsheet_summary(
                        pair.spreadsheet_record
                    )
                else:
                    spreadsheet_summary = cls._spreadsheet_group_summary(
                        pair.spreadsheet_records
                    )
                lines.append(
                    f"{index}. Spreadsheet: "
                    f"{spreadsheet_summary} | "
                    "Kintone ID: "
                    f"{cls._kintone_id(pair.kintone_record)}"
                )
            sections.append("\n".join(lines))

        if result.unmatched_spreadsheet_records:
            lines = ["UNMATCHED SPREADSHEET RECORDS"]
            for index, record in enumerate(
                result.unmatched_spreadsheet_records,
                start=1,
            ):
                lines.append(f"{index}. {cls._spreadsheet_summary(record)}")
            sections.append("\n".join(lines))

        if result.noncompleted_fallback_matches:
            lines = ["NON-COMPLETED FALLBACK MATCHES"]
            for index, pair in enumerate(
                result.noncompleted_fallback_matches,
                start=1,
            ):
                if len(pair.spreadsheet_records) == 1:
                    spreadsheet_summary = cls._spreadsheet_summary(
                        pair.spreadsheet_record
                    )
                else:
                    spreadsheet_summary = cls._spreadsheet_group_summary(
                        pair.spreadsheet_records
                    )
                lines.append(
                    f"{index}. Spreadsheet: {spreadsheet_summary} | "
                    f"Kintone ID: {cls._kintone_id(pair.kintone_record)}"
                )
            sections.append("\n".join(lines))

        if result.amount_only_fallback_matches:
            lines = ["UNIQUE AMOUNT-ONLY FALLBACK MATCHES"]
            for index, pair in enumerate(
                result.amount_only_fallback_matches,
                start=1,
            ):
                lines.append(
                    f"{index}. Spreadsheet: "
                    f"{cls._spreadsheet_summary(pair.spreadsheet_record)} | "
                    f"Kintone ID: {cls._kintone_id(pair.kintone_record)}"
                )
            sections.append("\n".join(lines))

        if result.unmatched_kintone_records:
            lines = ["UNMATCHED KINTONE RECORDS"]
            for index, record in enumerate(
                result.unmatched_kintone_records,
                start=1,
            ):
                lines.append(f"{index}. {cls._kintone_summary(record)}")
            sections.append("\n".join(lines))
        return "\n\n".join(sections)

    @staticmethod
    def _spreadsheet_summary(record) -> str:
        record_date = record.get("Date")
        if hasattr(record_date, "date"):
            record_date = record_date.date()
        return (
            f"Date: {str(record_date)[:10]} | "
            f"Payee/Payer: {record.get('Payee/Payer') or '-'} | "
            f"Amount: {record.get('Amount')}"
        )

    @staticmethod
    def _spreadsheet_group_summary(records) -> str:
        first = records[0]
        record_date = first.get("Date")
        if hasattr(record_date, "date"):
            record_date = record_date.date()
        combined_amount = sum(
            float(record.get("Amount") or 0) for record in records
        )
        row_numbers = ", ".join(
            str(record.get("__row_number__") or "?")
            for record in records
        )
        return (
            f"Rows: {row_numbers} | Date: {str(record_date)[:10]} | "
            f"Payee/Payer: {first.get('Payee/Payer') or '-'} | "
            f"Combined Amount: {combined_amount:.2f}"
        )

    @classmethod
    def _kintone_summary(cls, record) -> str:
        payee = cls.reconciliation_service_value(
            record,
            "Payee",
            "SINGLE_LINE_TEXT",
        )
        total = cls.reconciliation_service_value(
            record,
            "Total_Amount",
            "CALC",
        )
        updated = cls.reconciliation_service_value(
            record,
            "更新日時",
            "UPDATED_TIME",
        )
        return (
            f"Kintone ID: {cls._kintone_id(record)} | "
            f"Payee: {payee or '-'} | Total_Amount: {total} | "
            f"Updated: {updated or '-'}"
        )

    @staticmethod
    def reconciliation_service_value(record, code, field_type):
        field = record.get(code)
        if isinstance(field, dict) and "value" in field:
            return field.get("value")
        for candidate in record.values():
            if (
                isinstance(candidate, dict)
                and candidate.get("type") == field_type
            ):
                return candidate.get("value")
        return None

    @classmethod
    def _kintone_id(cls, record) -> str:
        value = cls.reconciliation_service_value(record, "$id", "__ID__")
        if value in (None, ""):
            value = cls.reconciliation_service_value(
                record,
                "レコード番号",
                "RECORD_NUMBER",
            )
        return "" if value in (None, "") else str(value)
