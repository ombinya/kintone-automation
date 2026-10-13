"""Dialog for manually choosing a Kintone record candidate."""

from datetime import datetime
from zoneinfo import ZoneInfo

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableView,
    QVBoxLayout,
)


class KintoneCandidateDialog(QDialog):
    """Present exact-amount Kintone candidates for manual selection."""

    def __init__(self, spreadsheet_records, candidates, parent=None) -> None:
        super().__init__(parent)
        if isinstance(spreadsheet_records, dict):
            spreadsheet_records = (spreadsheet_records,)
        self._spreadsheet_records = tuple(spreadsheet_records)
        self._candidates = sorted(
            candidates,
            key=self._updated_sort_value,
            reverse=True,
        )
        self._selected_record = None
        self.setWindowTitle("Select Kintone Record")
        self.setMinimumSize(1050, 420)

        layout = QVBoxLayout(self)
        combined_amount = sum(
            float(record.get("Amount") or 0)
            for record in self._spreadsheet_records
        )
        row_count_text = (
            "record"
            if len(self._spreadsheet_records) == 1
            else f"{len(self._spreadsheet_records)} combined records"
        )
        layout.addWidget(
            QLabel(
                f"Select the Kintone record for {row_count_text}: "
                f"{self._spreadsheet_records[0].get('Payee/Payer') or '-'} — "
                f"amount {combined_amount:g} (± KSh 5).",
                self,
            )
        )

        self.table = QTableView(self)
        self.model = QStandardItemModel(0, 5, self)
        self.model.setHorizontalHeaderLabels(
            ("Date", "Payee", "Amount", "Description", "Last Updated")
        )
        self.table.setModel(self.model)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        for record in self._candidates:
            items = [
                QStandardItem(str(self._field_value(record, "Date") or "")),
                QStandardItem(str(self._field_value(record, "Payee") or "")),
                QStandardItem(
                    str(self._field_value(record, "Total_Amount") or "")
                ),
                QStandardItem(self._description_text(record)),
                QStandardItem(self._updated_text(record)),
            ]
            items[2].setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.model.appendRow(items)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self._select_button = buttons.button(
            QDialogButtonBox.StandardButton.Ok
        )
        self._select_button.setText("Select")
        self._select_button.setEnabled(False)
        buttons.accepted.connect(self._accept_selection)
        buttons.rejected.connect(self.reject)
        self.table.selectionModel().selectionChanged.connect(
            self._selection_changed
        )
        self.table.doubleClicked.connect(
            lambda _index: self._accept_selection()
        )
        layout.addWidget(buttons)

    @property
    def selected_record(self):
        return self._selected_record

    def _selection_changed(self) -> None:
        self._select_button.setEnabled(
            bool(self.table.selectionModel().selectedRows())
        )

    def _accept_selection(self) -> None:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        self._selected_record = self._candidates[selected_rows[0].row()]
        self.accept()

    @staticmethod
    def _field_value(record, field_code):
        field = record.get(field_code)
        if isinstance(field, dict):
            return field.get("value")
        return None

    @classmethod
    def _updated_text(cls, record) -> str:
        value = cls._field_value(record, "更新日時")
        if not value:
            return ""
        try:
            updated = datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )
            return updated.astimezone(
                ZoneInfo("Africa/Nairobi")
            ).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return str(value)

    @classmethod
    def _updated_sort_value(cls, record) -> str:
        return str(cls._field_value(record, "更新日時") or "")

    @staticmethod
    def _description_text(record) -> str:
        table = record.get("テーブル")
        if not isinstance(table, dict) or table.get("type") != "SUBTABLE":
            table = next(
                (
                    field
                    for field in record.values()
                    if isinstance(field, dict)
                    and field.get("type") == "SUBTABLE"
                    and any(
                        "文字列__1行__4" in row.get("value", {})
                        for row in field.get("value", [])
                        if isinstance(row, dict)
                    )
                ),
                None,
            )
        if not isinstance(table, dict):
            return ""

        descriptions = []
        for row in table.get("value", []):
            if not isinstance(row, dict):
                continue
            row_values = row.get("value", {})
            if not isinstance(row_values, dict):
                continue
            description_field = row_values.get("文字列__1行__4")
            if not isinstance(description_field, dict):
                continue
            description = str(description_field.get("value") or "").strip()
            if description:
                descriptions.append(description)
        return " | ".join(descriptions)
