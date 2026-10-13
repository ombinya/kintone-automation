"""Read accounting records from Kintone."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
from urllib.parse import urlparse

import requests


class KintoneServiceError(RuntimeError):
    """An expected Kintone configuration or request failure."""


class KintoneService:
    """Fetch Kintone records used by spreadsheet reconciliation."""

    PAGE_SIZE = 500
    CANDIDATE_AMOUNT_TOLERANCE = Decimal("5")

    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    def get_records_for_period(
        self,
        month: int,
        year: int,
        payment_method: str,
    ) -> list[dict]:
        """Fetch all statuses updated within the selected calendar month."""
        updated_since, updated_before = self._period_boundaries(month, year)
        query_filter = (
            f'更新日時 >= "{updated_since}" '
            f'and 更新日時 < "{updated_before}" '
            f'and ラジオボタン in ("{payment_method}")'
        )
        return self._get_records(query_filter, payment_method)

    def get_records_outside_period(
        self,
        month: int,
        year: int,
        payment_method: str,
    ) -> list[dict]:
        """Fetch possible matches updated before or after the selected month."""
        updated_since, updated_before = self._period_boundaries(month, year)
        query_filter = (
            f'(更新日時 < "{updated_since}" '
            f'or 更新日時 >= "{updated_before}") '
            f'and ラジオボタン in ("{payment_method}")'
        )
        return self._get_records(query_filter, payment_method)

    def get_records_matching_amount(
        self,
        amount,
        payment_method: str,
    ) -> list[dict]:
        """Fetch same-payment-method records with an exact amount match."""
        try:
            numeric_amount = Decimal(str(amount).replace(",", ""))
        except (InvalidOperation, ValueError) as error:
            raise KintoneServiceError(
                "The selected spreadsheet record has an invalid amount."
            ) from error
        if not numeric_amount.is_finite():
            raise KintoneServiceError(
                "The selected spreadsheet record has an invalid amount."
            )

        minimum_amount = numeric_amount - self.CANDIDATE_AMOUNT_TOLERANCE
        maximum_amount = numeric_amount + self.CANDIDATE_AMOUNT_TOLERANCE
        query_filter = (
            f'Total_Amount >= {format(minimum_amount, "f")} '
            f'and Total_Amount <= {format(maximum_amount, "f")} '
            f'and ラジオボタン in ("{payment_method}")'
        )
        return self._get_records(
            query_filter,
            payment_method,
            order_direction="desc",
        )

    def get_record_by_id(self, record_id) -> dict:
        """Fetch one Kintone record by its record ID."""
        base_url, app_id, api_token = self._configuration()
        endpoint = f"{base_url}/record.json"
        try:
            response = requests.get(
                endpoint,
                headers={"X-Cybozu-API-Token": api_token},
                params={"app": app_id, "id": str(record_id), "lang": "en"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            raise KintoneServiceError(
                f"Kintone record {record_id} could not be downloaded."
            ) from error
        except ValueError as error:
            raise KintoneServiceError(
                "Kintone returned an invalid record response."
            ) from error
        record = payload.get("record")
        if not isinstance(record, dict):
            raise KintoneServiceError(
                f"Kintone record {record_id} was not returned."
            )
        return record

    def download_file(self, file_key: str, destination: Path) -> Path:
        """Download one Kintone attachment to an exact destination path."""
        base_url, _app_id, api_token = self._configuration()
        endpoint = f"{base_url}/file.json"
        temporary = destination.with_name(f".{destination.name}.part")
        try:
            response = requests.get(
                endpoint,
                headers={"X-Cybozu-API-Token": api_token},
                params={"fileKey": file_key},
                stream=True,
                timeout=self.timeout,
            )
            response.raise_for_status()
            with temporary.open("wb") as output:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        output.write(chunk)
            temporary.replace(destination)
        except (requests.RequestException, OSError) as error:
            raise KintoneServiceError(
                f"A Kintone attachment could not be saved as "
                f"{destination.name}."
            ) from error
        finally:
            if temporary.exists():
                temporary.unlink()
        return destination

    def _get_records(
        self,
        query_filter: str,
        payment_method: str,
        order_direction: str = "asc",
    ) -> list[dict]:
        base_url, app_id, api_token = self._configuration()
        if payment_method not in ("MPESA 1", "MPESA 2"):
            raise KintoneServiceError(
                f"Unsupported Kintone payment method: {payment_method!r}."
            )
        endpoint = f"{base_url}/records.json"
        if order_direction not in ("asc", "desc"):
            raise ValueError("Unsupported Kintone sort direction.")
        records = []
        offset = 0
        while True:
            query = (
                f"{query_filter} "
                f"order by 更新日時 {order_direction} limit {self.PAGE_SIZE} "
                f"offset {offset}"
            )
            try:
                response = requests.get(
                    endpoint,
                    headers={"X-Cybozu-API-Token": api_token},
                    params={"app": app_id, "lang": "en", "query": query},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                payload = response.json()
            except requests.RequestException as error:
                raise KintoneServiceError(
                    "Kintone records could not be downloaded. Check the "
                    "connection and API configuration, then try again."
                ) from error
            except ValueError as error:
                raise KintoneServiceError(
                    "Kintone returned an invalid response."
                ) from error

            batch = payload.get("records")
            if not isinstance(batch, list):
                message = payload.get("message") or "Unknown Kintone error."
                raise KintoneServiceError(str(message))

            records.extend(batch)
            if len(batch) < self.PAGE_SIZE:
                break
            offset += self.PAGE_SIZE

        return records

    @staticmethod
    def _period_boundaries(month: int, year: int) -> tuple[str, str]:
        period_start = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            period_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            period_end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        return (
            period_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            period_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    @staticmethod
    def _configuration() -> tuple[str, str, str]:
        file_values = KintoneService._file_configuration()
        subdomain = (
            os.getenv("KINTONE_SUBDOMAIN")
            or file_values.get("KINTONE_SUBDOMAIN", "")
        ).strip()
        app_id = (
            os.getenv("KINTONE_APP_ID")
            or file_values.get("KINTONE_APP_ID", "")
        ).strip()
        api_token = (
            os.getenv("KINTONE_API_TOKEN")
            or file_values.get("KINTONE_API_TOKEN", "")
        ).strip()
        missing = [
            name
            for name, value in (
                ("KINTONE_SUBDOMAIN", subdomain),
                ("KINTONE_APP_ID", app_id),
                ("KINTONE_API_TOKEN", api_token),
            )
            if not value
        ]
        if missing:
            raise KintoneServiceError(
                "Missing Kintone environment variable(s): "
                + ", ".join(missing)
                + "."
            )

        if "://" in subdomain:
            parsed = urlparse(subdomain)
            host = parsed.netloc
        else:
            host = subdomain
        host = host.strip().strip("/")
        if "." not in host:
            host = f"{host}.cybozu.com"
        return f"https://{host}/k/v1", app_id, api_token

    @staticmethod
    def _file_configuration() -> dict[str, str]:
        config_file = Path(__file__).resolve().parent.parent / "envars.txt"
        if not config_file.is_file():
            return {}

        values = {}
        try:
            lines = config_file.read_text(encoding="utf-8-sig").splitlines()
        except OSError as error:
            raise KintoneServiceError(
                "The Kintone configuration file could not be read."
            ) from error

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip()
            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in ('"', "'")
            ):
                value = value[1:-1]
            if name in {
                "KINTONE_SUBDOMAIN",
                "KINTONE_APP_ID",
                "KINTONE_API_TOKEN",
            }:
                values[name] = value
        return values
