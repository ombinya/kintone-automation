"""Controller for statement-to-spreadsheet reconciliation."""

from pathlib import Path

from PySide6.QtWidgets import QMessageBox

from services.spreadsheet_service import SpreadsheetServiceError


class ReconciliationController:
    def __init__(
        self,
        view,
        reconciliation_service,
        spreadsheet_service,
        statement_controller,
        spreadsheet_controller,
    ) -> None:
        self.view = view
        self.reconciliation_service = reconciliation_service
        self.spreadsheet_service = spreadsheet_service
        self.statement_controller = statement_controller
        self.spreadsheet_controller = spreadsheet_controller
        self.result = None

        self.view.reconcile_statement_spreadsheet_clicked.connect(
            self.reconcile
        )
        self.view.period_changed.connect(self.invalidate_result)

    def reconcile(self) -> None:
        self.view.set_reconciliation_complete(False)
        statement_transactions = (
            self.statement_controller.statement_transactions
        )
        spreadsheet_records = self.spreadsheet_controller.spreadsheet_records
        if statement_transactions is None or spreadsheet_records is None:
            QMessageBox.warning(
                self.view,
                "Files Not Validated",
                "Unlock and validate the statement, then validate the "
                "spreadsheet before reconciling.",
            )
            return

        missing_statement_transactions = (
            self.reconciliation_service.find_missing_statement_transactions(
                statement_transactions,
                spreadsheet_records,
            )
        )

        assignments = (
            self.reconciliation_service.find_missing_code_assignments(
                statement_transactions,
                spreadsheet_records,
            )
        )
        original_codes = [
            (
                assignment.spreadsheet_record,
                assignment.spreadsheet_record.get("Transaction Code"),
            )
            for assignment in assignments
        ]
        for assignment in assignments:
            assignment.spreadsheet_record["Transaction Code"] = (
                assignment.transaction_code
            )

        preliminary_result = self.reconciliation_service.reconcile(
            statement_transactions,
            spreadsheet_records,
        )
        for record, original_code in original_codes:
            record["Transaction Code"] = original_code

        if preliminary_result.unmatched_spreadsheet_records:
            self.result = None
            self.spreadsheet_controller.invalidate_validation()
            message_box = QMessageBox(self.view)
            message_box.setIcon(QMessageBox.Icon.Warning)
            message_box.setWindowTitle(
                "Spreadsheet Records Without Matches"
            )
            message_box.setText(
                f"{len(preliminary_result.unmatched_spreadsheet_records)} "
                "spreadsheet record(s) could not be matched to any "
                "statement transaction."
            )
            message_box.setInformativeText(
                "Review and correct the spreadsheet, save and close it, "
                "then validate it again before reconciling. Click Show "
                "Details to view the records."
            )
            message_box.setDetailedText(
                self._format_unmatched_spreadsheet_records(
                    preliminary_result.unmatched_spreadsheet_records
                )
            )
            message_box.exec()
            return

        updated_copy = None
        try:
            updated_copy = self.spreadsheet_service.save_updated_copy(
                self.spreadsheet_controller.spreadsheet_file_path,
                spreadsheet_records,
                assignments,
                missing_statement_transactions,
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
                "Unable to Update Spreadsheet",
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
        spreadsheet_records = self.spreadsheet_controller.spreadsheet_records
        self.view.set_spreadsheet_file_path(updated_path)
        self.view.set_spreadsheet_records(spreadsheet_records)

        self.result = self.reconciliation_service.reconcile(
            statement_transactions,
            spreadsheet_records,
        )
        reconciliation_complete = not (
            self.result.unmatched_statement_transactions
            or self.result.unmatched_spreadsheet_records
        )
        self.view.set_reconciliation_complete(reconciliation_complete)
        matched_spreadsheet_rows = sum(
            len(pair.spreadsheet_records)
            for pair in self.result.matched_pairs
        )
        matched_statement_transactions = sum(
            len(pair.statement_transactions)
            for pair in self.result.matched_pairs
        )
        combined_match_count = sum(
            len(pair.statement_transactions) > 1
            and len(pair.spreadsheet_records) == 1
            for pair in self.result.matched_pairs
        )
        if missing_statement_transactions:
            self._notify_added_records(
                missing_statement_transactions,
                Path(updated_copy).name,
            )
        QMessageBox.information(
            self.view,
            "Reconciliation Complete",
            "The statement and spreadsheet have been checked using "
            "transaction code, date, amount, and transaction charge.\n\n"
            f"Updated file: {Path(updated_copy).name}\n\n"
            f"Statement transactions: {len(statement_transactions)}\n"
            f"Spreadsheet records: {len(spreadsheet_records)}\n"
            "Matched statement transactions: "
            f"{matched_statement_transactions}\n"
            f"Matched spreadsheet records: {matched_spreadsheet_rows}\n"
            "Consolidated spreadsheet records detected: "
            f"{combined_match_count}\n"
            "Unmatched statement transactions: "
            f"{len(self.result.unmatched_statement_transactions)}\n"
            "Unmatched spreadsheet records: "
            f"{len(self.result.unmatched_spreadsheet_records)}",
        )

    def invalidate_result(self) -> None:
        self.result = None
        self.view.set_reconciliation_complete(False)

    def _notify_added_records(self, transactions, file_name: str) -> None:
        message_box = QMessageBox(self.view)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("New Spreadsheet Records Added")
        message_box.setText(
            f"{len(transactions)} new record(s) were added to "
            f"{file_name}."
        )
        message_box.setInformativeText(
            "Review the added records and complete any user-managed fields "
            "such as Account Code, Job Code, JC3, Description, and Remarks. "
            "Click Show Details to view the records."
        )
        message_box.setDetailedText(
            self._format_added_records(transactions)
        )
        message_box.exec()

    @staticmethod
    def _format_added_records(transactions) -> str:
        lines = []
        for index, transaction in enumerate(transactions, start=1):
            amount = transaction.get("Paid In")
            if amount is None:
                amount = transaction.get("Withdrawn")
            lines.append(
                f"{index}. Date: "
                f"{str(transaction.get('Completion Time'))[:10]} | "
                f"Transaction Code: {transaction.get('Receipt No.') or ''} | "
                f"Payee/Payer: {transaction.get('Payee') or '-'} | "
                "Amount: "
                f"{ReconciliationController._opposite_value(amount)} | "
                "Trans Chr.: "
                f"{ReconciliationController._opposite_value(transaction.get('Transaction charge'))}"
            )
        return "\n".join(lines)

    @staticmethod
    def _opposite_value(value):
        if value is None:
            return ""
        try:
            result = -float(str(value).replace(",", ""))
        except (TypeError, ValueError):
            return value
        if abs(result) < 0.005:
            result = 0.0
        return f"{result:.2f}"

    @staticmethod
    def _format_unmatched_spreadsheet_records(records) -> str:
        lines = []
        for index, record in enumerate(records, start=1):
            record_date = record.get("Date")
            if hasattr(record_date, "date"):
                record_date = record_date.date()
            lines.append(
                f"{index}. Date: {str(record_date)[:10]} | "
                f"Transaction Code: {record.get('Transaction Code') or ''} | "
                f"Payee/Payer: {record.get('Payee/Payer') or '-'} | "
                f"Amount: {ReconciliationController._spreadsheet_value(record.get('Amount'))} | "
                "Trans Chr.: "
                f"{ReconciliationController._spreadsheet_value(record.get('Trans Chr.'))}"
            )
        return "\n".join(lines)

    @staticmethod
    def _spreadsheet_value(value):
        if value is None:
            return ""
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return value
        if abs(numeric_value) < 0.005:
            numeric_value = 0.0
        return f"{numeric_value:.2f}"
