"""M-Pesa statement file operations."""

from calendar import month_name
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import pandas as pd
import tabula

from readers.statement_reader import StatementReader


@dataclass(frozen=True)
class StatementResult:
    workbook_path: Path
    transactions: tuple[dict, ...]
    month: int
    year: int
    stated_totals: dict
    calculated_totals: dict


class StatementServiceError(ValueError):
    """An expected statement selection or conversion failure."""


class StatementService:
    """Unlock an M-Pesa PDF and extract its tables to an Excel workbook."""

    def __init__(self, output_directory: Path) -> None:
        self.output_directory = Path(output_directory)

    def unlock_statement(
        self,
        file_path: str,
        password: str,
        month: int,
        year: int,
    ) -> StatementResult:
        source = Path(file_path)

        if not source.is_file():
            raise StatementServiceError("Select an M-Pesa statement PDF first.")
        if source.suffix.casefold() != ".pdf":
            raise StatementServiceError("The M-Pesa statement must be a PDF file.")
        if not password:
            raise StatementServiceError("Enter the statement password.")
        if not self.output_directory.is_dir():
            raise StatementServiceError(
                f"Output directory not found: {self.output_directory}"
            )

        output = self.output_directory / f"{source.stem}_unlocked.xlsx"
        temporary_output = output.with_name(
            f".{output.stem}.{uuid4().hex}.xlsx"
        )

        try:
            tables = tabula.read_pdf(
                str(source),
                pages="all",
                multiple_tables=True,
                password=password,
            )
            if not tables:
                raise StatementServiceError(
                    "The PDF was opened, but no statement tables were found."
                )

            with pd.ExcelWriter(temporary_output, engine="openpyxl") as writer:
                for index, table in enumerate(tables, start=1):
                    table.to_excel(
                        writer,
                        sheet_name=f"Table_{index}",
                        index=False,
                    )

            reader = StatementReader(temporary_output)
            transactions = reader.get_transactions()
            self._validate_period(transactions, month, year)

            temporary_output.replace(output)
            return StatementResult(
                workbook_path=output,
                transactions=tuple(transactions),
                month=month,
                year=year,
                stated_totals=dict(reader.stated_totals),
                calculated_totals=dict(reader.calculated_totals),
            )
        except StatementServiceError:
            raise
        except Exception as error:
            raise StatementServiceError(
                "The statement could not be unlocked. Check that the password "
                "is correct and that the selected file is a valid PDF."
            ) from error
        finally:
            if temporary_output.exists():
                temporary_output.unlink()

    @staticmethod
    def _validate_period(
        transactions: list[dict],
        expected_month: int,
        expected_year: int,
    ) -> None:
        expected_period = f"{month_name[expected_month]} {expected_year}"
        if not transactions:
            raise StatementServiceError(
                "No completed M-Pesa transactions were found in the PDF."
            )

        transaction_periods = Counter()
        for transaction in transactions:
            completion_date = StatementReader.completion_date(transaction)
            transaction_periods[
                (completion_date.year, completion_date.month)
            ] += 1

        invalid_count = sum(
            count
            for period, count in transaction_periods.items()
            if period != (expected_year, expected_month)
        )
        if invalid_count == 0:
            return

        found_periods = ", ".join(
            f"{month_name[month]} {year} ({count} transaction(s))"
            for (year, month), count in sorted(transaction_periods.items())
        )
        raise StatementServiceError(
            f"The statement does not match the selected period of "
            f"{expected_period}. {invalid_count} transaction(s) fall outside "
            f"that period. Periods found: {found_periods}. Select the correct "
            f"month and year, or choose a different statement file."
        )
