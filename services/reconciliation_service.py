"""Reconcile M-Pesa statement transactions with spreadsheet records."""

from dataclasses import dataclass
from datetime import date, datetime
import re

from readers.mpesa_record_reader import MpesaRecordReader


AMOUNT_TOLERANCE = 0.01


@dataclass(frozen=True)
class ReconciledPair:
    statement_transaction: dict
    spreadsheet_records: tuple[dict, ...]


@dataclass(frozen=True)
class ReconciliationResult:
    matched_pairs: tuple[ReconciledPair, ...]
    unmatched_statement_transactions: tuple[dict, ...]
    unmatched_spreadsheet_records: tuple[dict, ...]


@dataclass(frozen=True)
class TransactionCodeAssignment:
    statement_transaction: dict
    spreadsheet_record: dict
    method: str = "unique"


class ReconciliationService:
    """Perform deterministic, one-to-one transaction matching."""

    def reconcile(
        self,
        statement_transactions,
        spreadsheet_records,
    ) -> ReconciliationResult:
        unmatched_spreadsheet = list(spreadsheet_records)
        unmatched_statement = []
        matched_pairs = []

        for statement_transaction in statement_transactions:
            direct_match = next(
                (
                    record
                    for record in unmatched_spreadsheet
                    if self.transactions_match(
                        statement_transaction,
                        record,
                    )
                ),
                None,
            )
            if direct_match is not None:
                unmatched_spreadsheet.remove(direct_match)
                matched_pairs.append(
                    ReconciledPair(
                        statement_transaction,
                        (direct_match,),
                    )
                )
                continue

            group_matches = self._matching_consecutive_groups(
                statement_transaction,
                unmatched_spreadsheet,
                require_matching_code=True,
            )
            if len(group_matches) != 1:
                unmatched_statement.append(statement_transaction)
                continue

            matched_group = group_matches[0]
            matched_ids = {id(record) for record in matched_group}
            unmatched_spreadsheet = [
                record
                for record in unmatched_spreadsheet
                if id(record) not in matched_ids
            ]
            matched_pairs.append(
                ReconciledPair(statement_transaction, matched_group)
            )

        return ReconciliationResult(
            matched_pairs=tuple(matched_pairs),
            unmatched_statement_transactions=tuple(unmatched_statement),
            unmatched_spreadsheet_records=tuple(unmatched_spreadsheet),
        )

    def find_missing_code_assignments(
        self,
        statement_transactions,
        spreadsheet_records,
    ) -> tuple[TransactionCodeAssignment, ...]:
        """Find unambiguous legacy matches for blank transaction-code cells."""
        strict_result = self.reconcile(
            statement_transactions,
            spreadsheet_records,
        )
        remaining_statements = list(
            strict_result.unmatched_statement_transactions
        )
        remaining_records = [
            record
            for record in strict_result.unmatched_spreadsheet_records
            if record.get("Transaction Code") in (None, "")
        ]
        assignments = []

        while remaining_statements and remaining_records:
            candidates_by_statement = {
                id(statement): self._apply_record_payee_tiebreaker(
                    statement,
                    [
                        record
                        for record in remaining_records
                        if self._legacy_fields_match(statement, record)
                    ],
                )
                for statement in remaining_statements
            }
            candidate_use_count = {}
            for candidates in candidates_by_statement.values():
                for record in candidates:
                    candidate_use_count[id(record)] = (
                        candidate_use_count.get(id(record), 0) + 1
                    )

            round_assignments = []
            for statement in remaining_statements:
                candidates = candidates_by_statement[id(statement)]
                if (
                    len(candidates) == 1
                    and candidate_use_count[id(candidates[0])] == 1
                ):
                    round_assignments.append(
                        TransactionCodeAssignment(statement, candidates[0])
                    )

            if not round_assignments:
                break

            assignments.extend(round_assignments)
            assigned_statement_ids = {
                id(item.statement_transaction) for item in round_assignments
            }
            assigned_record_ids = {
                id(item.spreadsheet_record) for item in round_assignments
            }
            remaining_statements = [
                item
                for item in remaining_statements
                if id(item) not in assigned_statement_ids
            ]
            remaining_records = [
                item
                for item in remaining_records
                if id(item) not in assigned_record_ids
            ]

        while remaining_statements and remaining_records:
            candidates_by_statement = {
                id(statement): self._apply_group_payee_tiebreaker(
                    statement,
                    self._matching_consecutive_groups(
                        statement,
                        remaining_records,
                        require_matching_code=False,
                    ),
                )
                for statement in remaining_statements
            }
            record_use_count = {}
            for group_candidates in candidates_by_statement.values():
                for group in group_candidates:
                    for record in group:
                        record_use_count[id(record)] = (
                            record_use_count.get(id(record), 0) + 1
                        )

            accepted_groups = []
            for statement in remaining_statements:
                candidates = candidates_by_statement[id(statement)]
                if len(candidates) != 1:
                    continue
                group = candidates[0]
                if all(record_use_count[id(record)] == 1 for record in group):
                    accepted_groups.append((statement, group))

            if not accepted_groups:
                break

            assigned_statement_ids = set()
            assigned_record_ids = set()
            for statement, group in accepted_groups:
                assigned_statement_ids.add(id(statement))
                for record in group:
                    assigned_record_ids.add(id(record))
                    assignments.append(
                        TransactionCodeAssignment(
                            statement,
                            record,
                            method="split",
                        )
                    )

            remaining_statements = [
                statement
                for statement in remaining_statements
                if id(statement) not in assigned_statement_ids
            ]
            remaining_records = [
                record
                for record in remaining_records
                if id(record) not in assigned_record_ids
            ]

        for statement in remaining_statements:
            candidates = self._ordered_fallback_candidates(
                statement,
                remaining_records,
            )
            if not candidates:
                continue

            record = candidates[0]
            assignments.append(
                TransactionCodeAssignment(
                    statement,
                    record,
                    method="ordered",
                )
            )
            remaining_records = [
                item for item in remaining_records if item is not record
            ]

        return tuple(assignments)

    def find_missing_statement_transactions(
        self,
        statement_transactions,
        spreadsheet_records,
    ) -> tuple[dict, ...]:
        """Return statement transactions with no financial record candidate."""
        missing = []
        for statement in statement_transactions:
            has_direct_candidate = any(
                self._legacy_fields_match(statement, record)
                for record in spreadsheet_records
            )
            has_group_candidate = bool(
                self._matching_consecutive_groups(
                    statement,
                    spreadsheet_records,
                    require_matching_code=False,
                )
            )
            if not has_direct_candidate and not has_group_candidate:
                missing.append(statement)
        return tuple(missing)

    @classmethod
    def _ordered_fallback_candidates(
        cls,
        statement_transaction: dict,
        spreadsheet_records,
    ) -> list[dict]:
        candidates = [
            record
            for record in spreadsheet_records
            if cls._legacy_fields_match(statement_transaction, record)
        ]
        if not candidates:
            return []

        statement_has_payee = bool(
            cls._payee_tokens(statement_transaction.get("Payee"))
        )
        if statement_has_payee:
            return [
                record
                for record in candidates
                if cls._payees_match(
                    statement_transaction.get("Payee"),
                    record.get("Payee/Payer"),
                )
            ]

        return [
            record
            for record in candidates
            if not cls._payee_tokens(record.get("Payee/Payer"))
        ]

    @classmethod
    def _apply_record_payee_tiebreaker(
        cls,
        statement_transaction: dict,
        candidates: list[dict],
    ) -> list[dict]:
        if len(candidates) <= 1:
            return candidates

        matching_payees = [
            record
            for record in candidates
            if cls._payees_match(
                statement_transaction.get("Payee"),
                record.get("Payee/Payer"),
            )
        ]
        return matching_payees or candidates

    @classmethod
    def _apply_group_payee_tiebreaker(
        cls,
        statement_transaction: dict,
        candidate_groups: list[tuple[dict, ...]],
    ) -> list[tuple[dict, ...]]:
        if len(candidate_groups) <= 1:
            return candidate_groups

        matching_groups = [
            group
            for group in candidate_groups
            if any(
                cls._payees_match(
                    statement_transaction.get("Payee"),
                    record.get("Payee/Payer"),
                )
                for record in group
            )
        ]
        return matching_groups or candidate_groups

    @classmethod
    def _payees_match(cls, statement_payee, spreadsheet_payee) -> bool:
        statement_tokens = cls._payee_tokens(statement_payee)
        spreadsheet_tokens = cls._payee_tokens(spreadsheet_payee)
        if not statement_tokens or not spreadsheet_tokens:
            return False

        statement_set = set(statement_tokens)
        spreadsheet_set = set(spreadsheet_tokens)
        if statement_set <= spreadsheet_set or spreadsheet_set <= statement_set:
            return True

        statement_text = "".join(statement_tokens)
        spreadsheet_text = "".join(spreadsheet_tokens)
        shorter, longer = sorted(
            (statement_text, spreadsheet_text),
            key=len,
        )
        return len(shorter) >= 4 and shorter in longer

    @staticmethod
    def _payee_tokens(value) -> tuple[str, ...]:
        if value in (None, ""):
            return ()
        return tuple(
            re.findall(r"[a-z0-9]+", str(value).casefold())
        )

    @classmethod
    def _matching_consecutive_groups(
        cls,
        statement_transaction: dict,
        spreadsheet_records,
        require_matching_code: bool,
    ) -> list[tuple[dict, ...]]:
        statement_date = cls._date(
            statement_transaction.get("Completion Time")
        )
        receipt_number = statement_transaction.get("Receipt No.")
        eligible_records = []
        for record in spreadsheet_records:
            if cls._date(record.get("Date")) != statement_date:
                continue
            if require_matching_code and not cls._codes_match(
                receipt_number,
                record.get("Transaction Code"),
            ):
                continue
            eligible_records.append(record)

        matches = []
        for run in cls._consecutive_runs(eligible_records):
            for start in range(len(run)):
                for stop in range(start + 2, len(run) + 1):
                    candidate = tuple(run[start:stop])
                    if cls._group_financials_match(
                        statement_transaction,
                        candidate,
                    ):
                        matches.append(candidate)
        return matches

    @staticmethod
    def _consecutive_runs(records) -> list[list[dict]]:
        runs = []
        current_run = []
        for record in records:
            if current_run:
                previous = current_run[-1]
                same_worksheet = previous.get(
                    MpesaRecordReader.WORKSHEET_KEY
                ) == record.get(MpesaRecordReader.WORKSHEET_KEY)
                previous_row = previous.get(MpesaRecordReader.ROW_NUMBER_KEY)
                current_row = record.get(MpesaRecordReader.ROW_NUMBER_KEY)
                consecutive = (
                    previous_row is not None
                    and current_row is not None
                    and int(current_row) == int(previous_row) + 1
                )
                if not same_worksheet or not consecutive:
                    runs.append(current_run)
                    current_run = []
            current_run.append(record)
        if current_run:
            runs.append(current_run)
        return runs

    @classmethod
    def _group_financials_match(
        cls,
        statement_transaction: dict,
        spreadsheet_records,
    ) -> bool:
        statement_amount = cls._statement_amount(statement_transaction)
        if statement_amount is None:
            return False
        if any(
            record.get("Amount") is None
            for record in spreadsheet_records
        ):
            return False
        try:
            spreadsheet_amount = sum(
                float(record.get("Amount"))
                for record in spreadsheet_records
            )
            spreadsheet_charge = sum(
                float(record.get("Trans Chr."))
                for record in spreadsheet_records
                if record.get("Trans Chr.") is not None
            )
        except (TypeError, ValueError):
            return False

        statement_charge = statement_transaction.get("Transaction charge")
        normalized_statement_charge = (
            float(statement_charge) if statement_charge is not None else 0.0
        )
        return (
            cls._values_match(statement_amount, -spreadsheet_amount)
            and cls._values_match(
                normalized_statement_charge,
                -spreadsheet_charge,
            )
        )

    @classmethod
    def transactions_match(
        cls,
        statement_transaction: dict,
        spreadsheet_record: dict,
    ) -> bool:
        if not cls._codes_match(
            statement_transaction.get("Receipt No."),
            spreadsheet_record.get("Transaction Code"),
        ):
            return False

        return cls._legacy_fields_match(
            statement_transaction,
            spreadsheet_record,
        )

    @classmethod
    def _legacy_fields_match(
        cls,
        statement_transaction: dict,
        spreadsheet_record: dict,
    ) -> bool:
        if cls._date(statement_transaction.get("Completion Time")) != cls._date(
            spreadsheet_record.get("Date")
        ):
            return False

        statement_amount = cls._statement_amount(statement_transaction)
        spreadsheet_amount = spreadsheet_record.get("Amount")
        try:
            reversed_spreadsheet_amount = (
                -float(spreadsheet_amount)
                if spreadsheet_amount is not None
                else None
            )
        except (TypeError, ValueError):
            return False
        if not cls._values_match(
            statement_amount,
            reversed_spreadsheet_amount,
        ):
            return False

        statement_charge = statement_transaction.get("Transaction charge")
        spreadsheet_charge = spreadsheet_record.get("Trans Chr.")
        try:
            reversed_spreadsheet_charge = (
                -float(spreadsheet_charge)
                if spreadsheet_charge is not None
                else None
            )
        except (TypeError, ValueError):
            return False
        return cls._values_match(
            statement_charge,
            reversed_spreadsheet_charge,
        )

    @staticmethod
    def _codes_match(receipt_number, transaction_code) -> bool:
        if receipt_number in (None, "") or transaction_code in (None, ""):
            return False
        return str(receipt_number).strip().casefold() == str(
            transaction_code
        ).strip().casefold()

    @staticmethod
    def _date(value) -> date | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            normalized = value.strip()
            for date_format in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d",
            ):
                try:
                    return datetime.strptime(normalized, date_format).date()
                except ValueError:
                    continue
        return None

    @staticmethod
    def _statement_amount(transaction: dict):
        for title in ("Paid In", "Withdrawn"):
            value = transaction.get(title)
            if value is not None:
                return value
        return None

    @staticmethod
    def _values_match(left, right) -> bool:
        if left is None or right is None:
            return left is None and right is None
        try:
            return abs(float(left) - float(right)) <= AMOUNT_TOLERANCE
        except (TypeError, ValueError):
            return False
