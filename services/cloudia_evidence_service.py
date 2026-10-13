"""Generate monthly Cloudia evidence folders from matched spreadsheet rows."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import shutil
import unicodedata
from uuid import uuid4

import pymupdf
from PyPDF2 import PdfReader, PdfWriter

from services.kintone_service import KintoneServiceError


class CloudiaEvidenceServiceError(RuntimeError):
    """An expected Cloudia evidence generation failure."""


@dataclass(frozen=True)
class CloudiaEvidenceResult:
    output_folder: Path
    record_folder_count: int
    attachment_count: int
    request_page_count: int


class CloudiaEvidenceService:
    """Build a replaceable evidence tree for one selected calendar month."""

    INVALID_FILENAME_CHARACTERS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

    def __init__(self, project_directory: Path, kintone_service) -> None:
        self.project_directory = Path(project_directory).resolve()
        self.kintone_service = kintone_service

    def generate(
        self,
        spreadsheet_records,
        month: int,
        year: int,
        request_pdf,
    ):
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

        kintone_groups = []
        for record_id, records in grouped_records:
            kintone_record = self.kintone_service.get_record_by_id(record_id)
            kintone_groups.append((record_id, records, kintone_record))
        pdf_reader, request_pages = self._match_request_pages(
            request_pdf,
            kintone_groups,
        )

        staging_folder = self.project_directory / (
            f".{folder_name}.evidence-{uuid4().hex}"
        )
        attachment_count = 0
        try:
            staging_folder.mkdir()
            used_folder_names = set()
            for record_id, records, kintone_record in kintone_groups:
                record_folder_name = self._record_folder_name(records)
                if record_folder_name.casefold() in used_folder_names:
                    raise CloudiaEvidenceServiceError(
                        "Two matched transactions would create the same "
                        f"evidence folder: {record_folder_name}"
                    )
                used_folder_names.add(record_folder_name.casefold())
                record_folder = staging_folder / record_folder_name
                record_folder.mkdir()

                request_name = self._request_file_name(
                    kintone_record,
                    records,
                )
                self._write_request_page(
                    pdf_reader,
                    request_pages[record_id],
                    record_folder / request_name,
                )

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
            request_page_count=len(request_pages),
        )

    @classmethod
    def _match_request_pages(cls, request_pdf, kintone_groups):
        pdf_path = Path(request_pdf)
        if not pdf_path.is_file() or pdf_path.suffix.casefold() != ".pdf":
            raise CloudiaEvidenceServiceError(
                "Select a valid Kintone request PDF before generating evidence."
            )
        try:
            with pymupdf.open(pdf_path) as document:
                page_texts = [
                    cls._normalized_pdf_text(page.get_text("text"))
                    for page in document
                ]
            reader = PdfReader(str(pdf_path))
        except Exception as error:
            raise CloudiaEvidenceServiceError(
                "The selected Kintone request PDF could not be read."
            ) from error

        page_by_record = {}
        problems = []
        claimed_pages = {}
        for record_id, _spreadsheet_records, kintone_record in kintone_groups:
            tokens = cls._request_match_tokens(kintone_record)
            matching_pages = [
                index
                for index, page_text in enumerate(page_texts)
                if all(token in page_text for token in tokens)
            ]
            if len(matching_pages) != 1:
                payee = cls._field_value(kintone_record, "Payee") or "-"
                problems.append(
                    f"Kintone {record_id} ({payee}): "
                    f"{len(matching_pages)} matching pages"
                )
                continue
            page_index = matching_pages[0]
            if page_index in claimed_pages:
                problems.append(
                    f"Kintone {record_id} and {claimed_pages[page_index]} "
                    f"both match PDF page {page_index + 1}"
                )
                continue
            claimed_pages[page_index] = record_id
            page_by_record[record_id] = page_index

        if problems:
            details = "\n".join(problems[:20])
            if len(problems) > 20:
                details += f"\n...and {len(problems) - 20} more."
            raise CloudiaEvidenceServiceError(
                "The Kintone request PDF could not be matched uniquely:\n"
                + details
            )
        return reader, page_by_record

    @classmethod
    def _request_match_tokens(cls, record) -> tuple[str, ...]:
        values = [
            cls._field_value(record, "ラジオボタン"),
            cls._field_value(record, "Date"),
            cls._field_value(record, "Total_Amount"),
            cls._field_value(record, "Payee"),
        ]
        if any(value in (None, "") for value in values):
            raise CloudiaEvidenceServiceError(
                "A matched Kintone record is missing its payment method, "
                "date, amount, or payee."
            )
        tokens = [cls._normalized_pdf_text(value) for value in values]
        tokens.extend(cls._description_match_tokens(record))
        return tuple(token for token in tokens if token)

    @classmethod
    def _description_match_tokens(cls, record) -> tuple[str, ...]:
        table = record.get("テーブル")
        if not isinstance(table, dict):
            table = next(
                (
                    field
                    for field in record.values()
                    if isinstance(field, dict)
                    and field.get("type") == "SUBTABLE"
                    and any(
                        key in row.get("value", {})
                        for row in field.get("value", [])
                        if isinstance(row, dict)
                        for key in ("文字列__1行__4", "Description", "Item")
                    )
                ),
                {},
            )
        tokens = []
        for row in table.get("value", []) if isinstance(table, dict) else []:
            row_values = row.get("value", {}) if isinstance(row, dict) else {}
            separate_values = [
                cls._subtable_value(row_values, "Item"),
                cls._subtable_value(row_values, "Description"),
            ]
            if any(separate_values):
                tokens.extend(
                    cls._normalized_pdf_text(value)
                    for value in separate_values
                    if value
                )
            else:
                combined = cls._subtable_value(
                    row_values,
                    "文字列__1行__4",
                )
                if combined:
                    tokens.append(cls._normalized_pdf_text(combined))
        return tuple(tokens)

    @staticmethod
    def _subtable_value(row_values, code):
        field = row_values.get(code) if isinstance(row_values, dict) else None
        return field.get("value") if isinstance(field, dict) else None

    @staticmethod
    def _normalized_pdf_text(value) -> str:
        normalized = unicodedata.normalize("NFKC", str(value)).casefold()
        return "".join(character for character in normalized if character.isalnum())

    @staticmethod
    def _write_request_page(reader, page_index: int, destination: Path) -> None:
        try:
            writer = PdfWriter()
            writer.add_page(reader.pages[page_index])
            with destination.open("wb") as output:
                writer.write(output)
        except Exception as error:
            raise CloudiaEvidenceServiceError(
                f"PDF page {page_index + 1} could not be extracted."
            ) from error

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
        transaction_codes = cls._transaction_code_text(records)
        if record_date is None or not payee or not transaction_codes:
            raise CloudiaEvidenceServiceError(
                "Every matched spreadsheet group needs a date, payee, and "
                "transaction code before evidence can be generated."
            )
        amount = cls._spreadsheet_amount_label(records)
        name = (
            f"{record_date.isoformat()} {payee} "
            f"{amount} {transaction_codes}"
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
        amount = cls._file_amount_label(
            kintone_record,
            spreadsheet_records,
        )
        transaction_codes = cls._file_transaction_codes(spreadsheet_records)
        suffix = "" if attachment_index == 1 else f" {attachment_index}"
        base = cls._safe_name(
            f"Kintone {payee} {currency} {amount}{transaction_codes} "
            f"evidence{suffix}"
        )
        return f"{base}{extension.lower()}"

    @classmethod
    def _request_file_name(cls, kintone_record, spreadsheet_records) -> str:
        payee = cls._field_value(kintone_record, "Payee") or (
            spreadsheet_records[0].get("Payee/Payer")
        )
        currency = cls._field_value(kintone_record, "文字列__1行__2")
        if currency in (None, ""):
            raise CloudiaEvidenceServiceError(
                "A matched Kintone record does not contain a currency value."
            )
        amount = cls._file_amount_label(
            kintone_record,
            spreadsheet_records,
        )
        transaction_codes = cls._file_transaction_codes(spreadsheet_records)
        base = cls._safe_name(
            f"Kintone {payee} {currency} {amount}{transaction_codes} request"
        )
        return f"{base}.pdf"

    @classmethod
    def _file_amount_label(cls, kintone_record, spreadsheet_records) -> str:
        if len(spreadsheet_records) > 1:
            return cls._spreadsheet_amount_label(spreadsheet_records)

        kintone_amount = cls._field_value(kintone_record, "Total_Amount")
        try:
            amount = Decimal(str(kintone_amount).replace(",", ""))
        except (InvalidOperation, ValueError):
            amount = cls._combined_amount(spreadsheet_records)
        return cls._amount_text(amount)

    @classmethod
    def _spreadsheet_amount_label(cls, records) -> str:
        amounts = cls._spreadsheet_amounts(records)
        if len(amounts) == 1:
            return cls._amount_text(amounts[0])
        components = " + ".join(cls._amount_text(amount) for amount in amounts)
        return f"{components} = {cls._amount_text(sum(amounts, Decimal('0')))}"

    @staticmethod
    def _transaction_code_text(records) -> str:
        return ", ".join(CloudiaEvidenceService._transaction_codes(records))

    @staticmethod
    def _transaction_codes(records) -> tuple[str, ...]:
        codes = []
        seen = set()
        for record in records:
            code = str(record.get("Transaction Code") or "").strip()
            if code and code not in seen:
                seen.add(code)
                codes.append(code)
        return tuple(codes)

    @staticmethod
    def _file_transaction_codes(records) -> str:
        code_groups = CloudiaEvidenceService._transaction_codes(records)
        individual_codes = {
            code.casefold()
            for group in code_groups
            for code in group.split()
            if code
        }
        if len(individual_codes) <= 1:
            return ""
        return f" {', '.join(code_groups)}"

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
        return sum(CloudiaEvidenceService._spreadsheet_amounts(records), Decimal("0"))

    @staticmethod
    def _spreadsheet_amounts(records) -> tuple[Decimal, ...]:
        amounts = []
        for record in records:
            try:
                amounts.append(
                    Decimal(str(record.get("Amount")).replace(",", ""))
                )
            except (InvalidOperation, ValueError) as error:
                raise CloudiaEvidenceServiceError(
                    "A matched spreadsheet record has an invalid amount."
                ) from error
        return tuple(amounts)

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
