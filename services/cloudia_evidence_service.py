"""Generate monthly Cloudia evidence folders from matched spreadsheet rows."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import shutil
from uuid import uuid4

from services.kintone_service import KintoneServiceError


class CloudiaEvidenceServiceError(RuntimeError):
    """An expected Cloudia evidence generation failure."""


@dataclass(frozen=True)
class CloudiaEvidenceResult:
    output_folder: Path
    record_folder_count: int
    attachment_count: int


class CloudiaEvidenceService:
    """Build a replaceable evidence tree for one selected calendar month."""

    INVALID_FILENAME_CHARACTERS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

    def __init__(self, project_directory: Path, kintone_service) -> None:
        self.project_directory = Path(project_directory).resolve()
        self.kintone_service = kintone_service

    def generate(self, spreadsheet_records, month: int, year: int):
        folder_name = datetime(year, month, 1).strftime("%B %y")
        output_folder = self.project_directory / folder_name
        if output_folder.parent.resolve() != self.project_directory:
            raise CloudiaEvidenceServiceError(
                "The evidence output folder is outside the project directory."
            )

        grouped_records = self._matched_groups(
            spreadsheet_records,
            month,
            year,
        )
        if not grouped_records:
            raise CloudiaEvidenceServiceError(
                "There are no spreadsheet records with Kintone matches for "
                "the selected month."
            )

        staging_folder = self.project_directory / (
            f".{folder_name}.evidence-{uuid4().hex}"
        )
        attachment_count = 0
        try:
            staging_folder.mkdir()
            used_folder_names = set()
            for record_id, records in grouped_records:
                kintone_record = self.kintone_service.get_record_by_id(record_id)
                record_folder_name = self._record_folder_name(records)
                if record_folder_name.casefold() in used_folder_names:
                    raise CloudiaEvidenceServiceError(
                        "Two matched transactions would create the same "
                        f"evidence folder: {record_folder_name}"
                    )
                used_folder_names.add(record_folder_name.casefold())
                record_folder = staging_folder / record_folder_name
                record_folder.mkdir()

                attachments = self._attachments(kintone_record)
                for index, attachment in enumerate(attachments, start=1):
                    file_key = attachment.get("fileKey")
                    original_name = Path(str(attachment.get("name") or "")).name
                    extension = Path(original_name).suffix
                    if not file_key or not extension:
                        raise CloudiaEvidenceServiceError(
                            f"Kintone record {record_id} has an attachment "
                            "without a valid key or file extension."
                        )
                    evidence_name = self._evidence_file_name(
                        kintone_record,
                        records,
                        extension,
                        index,
                    )
                    self.kintone_service.download_file(
                        str(file_key),
                        record_folder / evidence_name,
                    )
                    attachment_count += 1

            if output_folder.exists():
                if not output_folder.is_dir():
                    output_folder.unlink()
                else:
                    shutil.rmtree(output_folder)
            staging_folder.replace(output_folder)
        except (CloudiaEvidenceServiceError, KintoneServiceError):
            raise
        except OSError as error:
            raise CloudiaEvidenceServiceError(
                "The Cloudia evidence folder could not be created or replaced."
            ) from error
        finally:
            if staging_folder.exists():
                shutil.rmtree(staging_folder, ignore_errors=True)

        return CloudiaEvidenceResult(
            output_folder=output_folder,
            record_folder_count=len(grouped_records),
            attachment_count=attachment_count,
        )

    @classmethod
    def _matched_groups(cls, records, month: int, year: int):
        grouped = {}
        order = []
        for record in records or ():
            record_id = record.get("Kintone Record ID")
            record_date = cls._date(record.get("Date"))
            if (
                record_id in (None, "")
                or record_date is None
                or record_date.month != month
                or record_date.year != year
            ):
                continue
            key = str(record_id).strip()
            if key not in grouped:
                grouped[key] = []
                order.append(key)
            grouped[key].append(record)
        return tuple((key, tuple(grouped[key])) for key in order)

    @classmethod
    def _record_folder_name(cls, records) -> str:
        first = records[0]
        record_date = cls._date(first.get("Date"))
        payee = str(first.get("Payee/Payer") or "").strip()
        transaction_codes = [
            str(record.get("Transaction Code") or "").strip()
            for record in records
            if record.get("Transaction Code") not in (None, "")
        ]
        if record_date is None or not payee or not transaction_codes:
            raise CloudiaEvidenceServiceError(
                "Every matched spreadsheet group needs a date, payee, and "
                "transaction code before evidence can be generated."
            )
        amount = cls._combined_amount(records)
        name = (
            f"{record_date.isoformat()} {payee} "
            f"{cls._amount_text(amount)} {transaction_codes[0]}"
        )
        return cls._safe_name(name)

    @classmethod
    def _evidence_file_name(
        cls,
        kintone_record,
        spreadsheet_records,
        extension: str,
        attachment_index: int,
    ) -> str:
        payee = cls._field_value(kintone_record, "Payee") or (
            spreadsheet_records[0].get("Payee/Payer")
        )
        currency = cls._field_value(kintone_record, "文字列__1行__2")
        if currency in (None, ""):
            raise CloudiaEvidenceServiceError(
                "A matched Kintone record does not contain a currency value."
            )
        kintone_amount = cls._field_value(kintone_record, "Total_Amount")
        try:
            amount = Decimal(str(kintone_amount).replace(",", ""))
        except (InvalidOperation, ValueError):
            amount = cls._combined_amount(spreadsheet_records)
        suffix = "" if attachment_index == 1 else f" {attachment_index}"
        base = cls._safe_name(
            f"Kintone {payee} {currency} {cls._amount_text(amount)} "
            f"evidence{suffix}"
        )
        return f"{base}{extension.lower()}"

    @staticmethod
    def _attachments(record):
        field = record.get("添付ファイル")
        if not isinstance(field, dict):
            field = next(
                (
                    value
                    for value in record.values()
                    if isinstance(value, dict) and value.get("type") == "FILE"
                ),
                {},
            )
        attachments = field.get("value", []) if isinstance(field, dict) else []
        return attachments if isinstance(attachments, list) else []

    @staticmethod
    def _field_value(record, code):
        field = record.get(code)
        return field.get("value") if isinstance(field, dict) else None

    @staticmethod
    def _date(value) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _combined_amount(records) -> Decimal:
        total = Decimal("0")
        for record in records:
            try:
                total += Decimal(str(record.get("Amount")).replace(",", ""))
            except (InvalidOperation, ValueError) as error:
                raise CloudiaEvidenceServiceError(
                    "A matched spreadsheet record has an invalid amount."
                ) from error
        return total

    @staticmethod
    def _amount_text(amount: Decimal) -> str:
        text = format(amount, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"

    @classmethod
    def _safe_name(cls, value) -> str:
        name = cls.INVALID_FILENAME_CHARACTERS.sub("_", str(value))
        name = " ".join(name.split()).rstrip(". ")
        return name[:180] or "Evidence"
