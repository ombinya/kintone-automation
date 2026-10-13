"""Reconcile spreadsheet records with Kintone accounting records."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
import re

from readers.mpesa_record_reader import MpesaRecordReader


AMOUNT_TOLERANCE = Decimal("5.00")
PAYEE_SIMILARITY_MINIMUM = 0.80


@dataclass(frozen=True)
class SpreadsheetKintoneMatch:
    spreadsheet_records: tuple[dict, ...]
    kintone_record: dict

    @property
    def spreadsheet_record(self) -> dict:
        """Retain convenient access for single-record match consumers."""
        return self.spreadsheet_records[0]


@dataclass(frozen=True)
class SpreadsheetKintoneResult:
    matched_pairs: tuple[SpreadsheetKintoneMatch, ...]
    unmatched_spreadsheet_records: tuple[dict, ...]
    ignored_negative_spreadsheet_records: tuple[dict, ...]
    unmatched_kintone_records: tuple[dict, ...]
    excluded_old_kintone_records: tuple[dict, ...]
    excluded_late_kintone_records: tuple[dict, ...]
    excluded_payment_method_records: tuple[dict, ...]
    excluded_incomplete_kintone_records: tuple[dict, ...]
    noncompleted_fallback_matches: tuple[SpreadsheetKintoneMatch, ...]
    amount_only_fallback_matches: tuple[SpreadsheetKintoneMatch, ...]


class KintoneReconciliationService:
    """Match spreadsheet Amount to Kintone Total_Amount with other rules."""

    def reconcile(
        self,
        spreadsheet_records,
        kintone_records,
        month: int,
        year: int,
        payment_method: str,
        outside_kintone_records=(),
        allow_incomplete_fallback: bool = False,
    ) -> SpreadsheetKintoneResult:
        threshold = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            period_end = datetime(
                year + 1,
                1,
                1,
                tzinfo=timezone.utc,
            )
        else:
            period_end = datetime(
                year,
                month + 1,
                1,
                tzinfo=timezone.utc,
            )
        eligible_kintone = []
        excluded_old = []
        excluded_late = []
        excluded_payment_method = []
        excluded_incomplete = []
        for record in kintone_records:
            updated_at = self.updated_at(record)
            if updated_at is None or updated_at < threshold:
                excluded_old.append(record)
            elif updated_at >= period_end:
                excluded_late.append(record)
            elif self.payment_method(record) != payment_method:
                excluded_payment_method.append(record)
            elif self.status(record) != "Completed":
                excluded_incomplete.append(record)
            else:
                eligible_kintone.append(record)

        unmatched_kintone = list(eligible_kintone)
        unmatched_spreadsheet = []
        ignored_negative_spreadsheet = []
        matches = []
        for spreadsheet_record in spreadsheet_records:
            spreadsheet_amount = self._money(
                spreadsheet_record.get("Amount")
            )
            if spreadsheet_amount is not None and spreadsheet_amount < 0:
                ignored_negative_spreadsheet.append(spreadsheet_record)
                continue

            candidate_indexes = [
                index
                for index, kintone_record in enumerate(unmatched_kintone)
                if self.records_match(
                    spreadsheet_record,
                    kintone_record,
                    threshold,
                    period_end,
                    payment_method,
                )
            ]
            similar_spreadsheet_count = sum(
                self._spreadsheet_records_similar(
                    spreadsheet_record,
                    candidate,
                )
                for candidate in spreadsheet_records
            )
            if (
                similar_spreadsheet_count > 1
                or len(candidate_indexes) > 1
            ):
                candidate_indexes = [
                    index
                    for index in candidate_indexes
                    if self._dates_match(
                        spreadsheet_record,
                        unmatched_kintone[index],
                    )
                ]
            match_index = self._select_candidate_index(
                spreadsheet_record,
                unmatched_kintone,
                candidate_indexes,
            )
            if match_index is None:
                unmatched_spreadsheet.append(spreadsheet_record)
                continue

            kintone_record = unmatched_kintone.pop(match_index)
            matches.append(
                SpreadsheetKintoneMatch(
                    (spreadsheet_record,),
                    kintone_record,
                )
            )

        group_matches = self._match_consecutive_groups(
            unmatched_spreadsheet,
            unmatched_kintone,
        )
        matches.extend(group_matches)
        matched_spreadsheet_ids = {
            id(record)
            for match in group_matches
            for record in match.spreadsheet_records
        }
        matched_kintone_ids = {
            id(match.kintone_record) for match in group_matches
        }
        unmatched_spreadsheet = [
            record
            for record in unmatched_spreadsheet
            if id(record) not in matched_spreadsheet_ids
        ]
        unmatched_kintone = [
            record
            for record in unmatched_kintone
            if id(record) not in matched_kintone_ids
        ]

        fallback_matches = []
        amount_only_matches = []
        if allow_incomplete_fallback and unmatched_spreadsheet:
            (
                fallback_matches,
                unmatched_spreadsheet,
                excluded_incomplete,
            ) = self._match_incomplete_fallback(
                unmatched_spreadsheet,
                excluded_incomplete,
                outside_kintone_records,
                spreadsheet_records,
                threshold,
                period_end,
                payment_method,
            )
            matches.extend(fallback_matches)

        if allow_incomplete_fallback and unmatched_spreadsheet:
            (
                amount_only_matches,
                unmatched_spreadsheet,
                unmatched_kintone,
                excluded_incomplete,
            ) = self._match_unique_amount_fallback(
                unmatched_spreadsheet,
                unmatched_kintone,
                excluded_incomplete,
                tuple(kintone_records) + tuple(outside_kintone_records),
                payment_method,
            )
            matches.extend(amount_only_matches)

        return SpreadsheetKintoneResult(
            matched_pairs=tuple(matches),
            unmatched_spreadsheet_records=tuple(unmatched_spreadsheet),
            ignored_negative_spreadsheet_records=tuple(
                ignored_negative_spreadsheet
            ),
            unmatched_kintone_records=tuple(unmatched_kintone),
            excluded_old_kintone_records=tuple(excluded_old),
            excluded_late_kintone_records=tuple(excluded_late),
            excluded_payment_method_records=tuple(
                excluded_payment_method
            ),
            excluded_incomplete_kintone_records=tuple(
                excluded_incomplete
            ),
            noncompleted_fallback_matches=tuple(fallback_matches),
            amount_only_fallback_matches=tuple(amount_only_matches),
        )

    @classmethod
    def records_match(
        cls,
        spreadsheet_record,
        kintone_record,
        threshold,
        period_end,
        payment_method: str,
        require_completed: bool = True,
    ) -> bool:
        updated_at = cls.updated_at(kintone_record)
        if (
            updated_at is None
            or updated_at < threshold
            or updated_at >= period_end
        ):
            return False
        if cls.payment_method(kintone_record) != payment_method:
            return False
        if require_completed and cls.status(kintone_record) != "Completed":
            return False

        spreadsheet_amount = cls._money(
            spreadsheet_record.get("Amount")
        )
        kintone_total = cls._money(
            cls._field_value(kintone_record, "Total_Amount", "CALC")
        )
        if spreadsheet_amount is None or kintone_total is None:
            return False
        if spreadsheet_amount < 0:
            return False

        kintone_payee = cls._payee(
            cls._field_value(kintone_record, "Payee", "SINGLE_LINE_TEXT")
        )
        spreadsheet_payee = cls._payee(
            spreadsheet_record.get("Payee/Payer")
        )
        if not cls._payees_match(spreadsheet_payee, kintone_payee):
            return False
        return abs(spreadsheet_amount - kintone_total) <= AMOUNT_TOLERANCE

    @classmethod
    def _match_incomplete_fallback(
        cls,
        spreadsheet_records,
        incomplete_kintone_records,
        outside_kintone_records,
        all_spreadsheet_records,
        threshold,
        period_end,
        payment_method,
    ):
        """Match non-Completed records only if no outside-period twin exists."""
        remaining_spreadsheet = list(spreadsheet_records)
        remaining_kintone = list(incomplete_kintone_records)
        outside_records = list(outside_kintone_records)
        matches = []

        for spreadsheet_record in list(remaining_spreadsheet):
            candidate_indexes = [
                index
                for index, kintone_record in enumerate(remaining_kintone)
                if cls.records_match(
                    spreadsheet_record,
                    kintone_record,
                    threshold,
                    period_end,
                    payment_method,
                    require_completed=False,
                )
                and not cls._has_outside_individual_candidate(
                    spreadsheet_record,
                    outside_records,
                    payment_method,
                )
            ]
            similar_spreadsheet_count = sum(
                cls._spreadsheet_records_similar(
                    spreadsheet_record,
                    candidate,
                )
                for candidate in all_spreadsheet_records
            )
            if similar_spreadsheet_count > 1 or len(candidate_indexes) > 1:
                candidate_indexes = [
                    index
                    for index in candidate_indexes
                    if cls._dates_match(
                        spreadsheet_record,
                        remaining_kintone[index],
                    )
                ]
            match_index = cls._select_candidate_index(
                spreadsheet_record,
                remaining_kintone,
                candidate_indexes,
            )
            if match_index is None:
                continue

            kintone_record = remaining_kintone.pop(match_index)
            remaining_spreadsheet = [
                record
                for record in remaining_spreadsheet
                if record is not spreadsheet_record
            ]
            matches.append(
                SpreadsheetKintoneMatch((spreadsheet_record,), kintone_record)
            )

        group_matches = cls._match_consecutive_groups(
            remaining_spreadsheet,
            remaining_kintone,
            outside_records=outside_records,
            payment_method=payment_method,
        )
        matches.extend(group_matches)
        matched_spreadsheet_ids = {
            id(record)
            for match in group_matches
            for record in match.spreadsheet_records
        }
        matched_kintone_ids = {
            id(match.kintone_record) for match in group_matches
        }
        remaining_spreadsheet = [
            record
            for record in remaining_spreadsheet
            if id(record) not in matched_spreadsheet_ids
        ]
        remaining_kintone = [
            record
            for record in remaining_kintone
            if id(record) not in matched_kintone_ids
        ]
        return matches, remaining_spreadsheet, remaining_kintone

    @classmethod
    def _has_outside_individual_candidate(
        cls,
        spreadsheet_record,
        outside_records,
        payment_method,
    ) -> bool:
        return any(
            cls.payment_method(record) == payment_method
            and cls._amount_and_payee_match(spreadsheet_record, record)
            for record in outside_records
        )

    @classmethod
    def _amount_and_payee_match(cls, spreadsheet_record, kintone_record):
        spreadsheet_amount = cls._money(spreadsheet_record.get("Amount"))
        kintone_total = cls._money(
            cls._field_value(kintone_record, "Total_Amount", "CALC")
        )
        if (
            spreadsheet_amount is None
            or spreadsheet_amount < 0
            or kintone_total is None
            or abs(spreadsheet_amount - kintone_total) > AMOUNT_TOLERANCE
        ):
            return False
        spreadsheet_payee = cls._payee(
            spreadsheet_record.get("Payee/Payer")
        )
        kintone_payee = cls._payee(
            cls._field_value(kintone_record, "Payee", "SINGLE_LINE_TEXT")
        )
        return cls._payees_match(spreadsheet_payee, kintone_payee)

    @classmethod
    def _match_unique_amount_fallback(
        cls,
        spreadsheet_records,
        completed_kintone_records,
        incomplete_kintone_records,
        all_kintone_records,
        payment_method,
    ):
        """Match an exact amount only when it is globally unique for MPESA."""
        remaining_spreadsheet = list(spreadsheet_records)
        remaining_completed = list(completed_kintone_records)
        remaining_incomplete = list(incomplete_kintone_records)
        matches = []

        for spreadsheet_record in list(remaining_spreadsheet):
            amount = cls._money(spreadsheet_record.get("Amount"))
            if amount is None or amount < 0:
                continue

            global_candidates = [
                record
                for record in all_kintone_records
                if cls.payment_method(record) == payment_method
                and cls._money(
                    cls._field_value(record, "Total_Amount", "CALC")
                )
                == amount
            ]
            if len(global_candidates) != 1:
                continue

            selected = global_candidates[0]
            if not any(
                record is selected
                for record in remaining_completed + remaining_incomplete
            ):
                continue

            matches.append(
                SpreadsheetKintoneMatch((spreadsheet_record,), selected)
            )
            remaining_spreadsheet = [
                record
                for record in remaining_spreadsheet
                if record is not spreadsheet_record
            ]
            remaining_completed = [
                record
                for record in remaining_completed
                if record is not selected
            ]
            remaining_incomplete = [
                record
                for record in remaining_incomplete
                if record is not selected
            ]

        return (
            matches,
            remaining_spreadsheet,
            remaining_completed,
            remaining_incomplete,
        )

    @classmethod
    def _match_consecutive_groups(
        cls,
        spreadsheet_records,
        kintone_records,
        outside_records=(),
        payment_method: str | None = None,
    ) -> list[SpreadsheetKintoneMatch]:
        remaining_spreadsheet = list(spreadsheet_records)
        remaining_kintone = list(kintone_records)
        matches = []

        while remaining_spreadsheet and remaining_kintone:
            selected_group = None
            selected_kintone = None
            for group in cls._candidate_groups(remaining_spreadsheet):
                candidates = [
                    record
                    for record in remaining_kintone
                    if cls._group_matches_kintone(group, record)
                    and not cls._has_outside_group_candidate(
                        group,
                        outside_records,
                        payment_method,
                    )
                ]
                selected_kintone = cls._select_kintone_by_payee(
                    group[0].get("Payee/Payer"),
                    candidates,
                )
                if selected_kintone is not None:
                    selected_group = group
                    break

            if selected_group is None or selected_kintone is None:
                break

            matches.append(
                SpreadsheetKintoneMatch(
                    selected_group,
                    selected_kintone,
                )
            )
            selected_ids = {id(record) for record in selected_group}
            remaining_spreadsheet = [
                record
                for record in remaining_spreadsheet
                if id(record) not in selected_ids
            ]
            remaining_kintone = [
                record
                for record in remaining_kintone
                if record is not selected_kintone
            ]

        return matches

    @classmethod
    def _has_outside_group_candidate(
        cls,
        group,
        outside_records,
        payment_method,
    ) -> bool:
        return any(
            (
                payment_method is None
                or cls.payment_method(record) == payment_method
            )
            and cls._group_matches_kintone(group, record)
            for record in outside_records
        )

    @classmethod
    def _candidate_groups(cls, records):
        for run in cls._consecutive_similar_runs(records):
            for start in range(len(run)):
                for stop in range(start + 2, len(run) + 1):
                    yield tuple(run[start:stop])

    @classmethod
    def _consecutive_similar_runs(cls, records) -> list[list[dict]]:
        runs = []
        current_run = []
        for record in records:
            if current_run and not cls._records_can_group(
                current_run[-1],
                record,
            ):
                if len(current_run) >= 2:
                    runs.append(current_run)
                current_run = []
            current_run.append(record)
        if len(current_run) >= 2:
            runs.append(current_run)
        return runs

    @classmethod
    def _records_can_group(cls, previous, current) -> bool:
        previous_row = previous.get(MpesaRecordReader.ROW_NUMBER_KEY)
        current_row = current.get(MpesaRecordReader.ROW_NUMBER_KEY)
        try:
            rows_are_consecutive = int(current_row) == int(previous_row) + 1
        except (TypeError, ValueError):
            return False
        if not rows_are_consecutive:
            return False
        if previous.get(MpesaRecordReader.WORKSHEET_KEY) != current.get(
            MpesaRecordReader.WORKSHEET_KEY
        ):
            return False
        if cls._date(previous.get("Date")) != cls._date(current.get("Date")):
            return False
        previous_payee = cls._payee(previous.get("Payee/Payer"))
        current_payee = cls._payee(current.get("Payee/Payer"))
        return bool(previous_payee) and previous_payee == current_payee

    @classmethod
    def _group_matches_kintone(cls, group, kintone_record) -> bool:
        group_payee = cls._payee(group[0].get("Payee/Payer"))
        kintone_payee = cls._payee(
            cls._field_value(kintone_record, "Payee", "SINGLE_LINE_TEXT")
        )
        if not cls._payees_match(group_payee, kintone_payee):
            return False

        amounts = [cls._money(record.get("Amount")) for record in group]
        if any(amount is None or amount < 0 for amount in amounts):
            return False
        kintone_total = cls._money(
            cls._field_value(kintone_record, "Total_Amount", "CALC")
        )
        if kintone_total is None:
            return False
        return abs(sum(amounts, Decimal("0")) - kintone_total) <= (
            AMOUNT_TOLERANCE
        )

    @classmethod
    def updated_at(cls, record) -> datetime | None:
        value = cls._field_value(record, "更新日時", "UPDATED_TIME")
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @classmethod
    def record_id(cls, record) -> str:
        value = cls._field_value(record, "$id", "__ID__")
        if value in (None, ""):
            value = cls._field_value(record, "レコード番号", "RECORD_NUMBER")
        return "" if value in (None, "") else str(value)

    @classmethod
    def payment_method(cls, record) -> str:
        value = cls._field_value(
            record,
            "ラジオボタン",
            "RADIO_BUTTON",
        )
        return "" if value in (None, "") else str(value).strip()

    @classmethod
    def status(cls, record) -> str:
        value = cls._field_value(record, "ステータス", "STATUS")
        return "" if value in (None, "") else str(value).strip()

    @classmethod
    def _spreadsheet_records_similar(cls, left, right) -> bool:
        left_amount = cls._money(left.get("Amount"))
        right_amount = cls._money(right.get("Amount"))
        if left_amount is None or right_amount is None:
            return False
        if left_amount < 0 or right_amount < 0:
            return False
        if abs(left_amount - right_amount) > AMOUNT_TOLERANCE:
            return False
        left_payee = cls._payee(left.get("Payee/Payer"))
        right_payee = cls._payee(right.get("Payee/Payer"))
        return bool(left_payee) and left_payee == right_payee

    @classmethod
    def _dates_match(cls, spreadsheet_record, kintone_record) -> bool:
        spreadsheet_date = cls._date(spreadsheet_record.get("Date"))
        updated_at = cls.updated_at(kintone_record)
        return (
            spreadsheet_date is not None
            and updated_at is not None
            and spreadsheet_date == updated_at.date()
        )

    @staticmethod
    def _date(value) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            normalized = value.strip()
            for date_format in (
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
            ):
                try:
                    return datetime.strptime(
                        normalized,
                        date_format,
                    ).date()
                except ValueError:
                    continue
        return None

    @staticmethod
    def _field_value(record, field_code: str, field_type: str):
        field = record.get(field_code)
        if isinstance(field, dict) and "value" in field:
            return field.get("value")
        if field_type not in ("UPDATED_TIME", "__ID__", "RECORD_NUMBER"):
            return None
        for candidate in record.values():
            if (
                isinstance(candidate, dict)
                and candidate.get("type") == field_type
            ):
                return candidate.get("value")
        return None

    @staticmethod
    def _payee(value) -> str:
        if value in (None, ""):
            return ""
        normalized = re.sub(
            r"[_\W]+",
            " ",
            str(value).casefold(),
            flags=re.UNICODE,
        )
        return " ".join(normalized.split())

    @classmethod
    def _payees_match(cls, left: str, right: str) -> bool:
        if not left or not right:
            return False
        if cls._payees_contain(left, right):
            return True
        return SequenceMatcher(None, left, right).ratio() >= (
            PAYEE_SIMILARITY_MINIMUM
        )

    @staticmethod
    def _payees_contain(left: str, right: str) -> bool:
        return bool(left and right) and (left in right or right in left)

    @classmethod
    def _select_candidate_index(
        cls,
        spreadsheet_record,
        kintone_records,
        candidate_indexes,
    ):
        spreadsheet_payee = cls._payee(
            spreadsheet_record.get("Payee/Payer")
        )
        candidates = [
            (index, kintone_records[index]) for index in candidate_indexes
        ]
        selected = cls._select_kintone_by_payee(
            spreadsheet_payee,
            [record for _, record in candidates],
        )
        if selected is None:
            return None
        return next(
            index for index, record in candidates if record is selected
        )

    @classmethod
    def _select_kintone_by_payee(cls, payee, candidates):
        if not candidates:
            return None
        normalized_payee = cls._payee(payee)
        strict_candidates = [
            record
            for record in candidates
            if cls._payees_contain(
                normalized_payee,
                cls._payee(
                    cls._field_value(
                        record,
                        "Payee",
                        "SINGLE_LINE_TEXT",
                    )
                ),
            )
        ]
        if strict_candidates:
            return strict_candidates[0]
        if len(candidates) == 1:
            return candidates[0]

        candidate_payees = {
            cls._payee(
                cls._field_value(
                    record,
                    "Payee",
                    "SINGLE_LINE_TEXT",
                )
            )
            for record in candidates
        }
        if len(candidate_payees) == 1:
            return candidates[0]
        return None

    @staticmethod
    def _money(value) -> Decimal | None:
        if value in (None, ""):
            return None
        try:
            return Decimal(str(value).replace(",", ""))
        except (InvalidOperation, ValueError):
            return None
