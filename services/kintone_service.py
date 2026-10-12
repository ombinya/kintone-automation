"""Read accounting records from Kintone."""

from datetime import datetime, timezone
import os
from pathlib import Path
from urllib.parse import urlparse

import requests


class KintoneServiceError(RuntimeError):
    """An expected Kintone configuration or request failure."""


class KintoneService:
    """Fetch Kintone records updated within the selected calendar month."""

    PAGE_SIZE = 500

    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    def get_records_for_period(
        self,
        month: int,
        year: int,
        payment_method: str,
    ) -> list[dict]:
        base_url, app_id, api_token = self._configuration()
        if payment_method not in ("MPESA 1", "MPESA 2"):
            raise KintoneServiceError(
                f"Unsupported Kintone payment method: {payment_method!r}."
            )
        endpoint = f"{base_url}/records.json"
        updated_since = datetime(
            year,
            month,
            1,
            tzinfo=timezone.utc,
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
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
        updated_before = period_end.strftime("%Y-%m-%dT%H:%M:%SZ")

        records = []
        offset = 0
        while True:
            query = (
                'ステータス in ("Completed") '
                f'and 更新日時 >= "{updated_since}" '
                f'and 更新日時 < "{updated_before}" '
                f'and ラジオボタン in ("{payment_method}") '
                f"order by 更新日時 asc limit {self.PAGE_SIZE} "
                f"offset {offset}"
            )
            try:
                response = requests.get(
                    endpoint,
                    headers={"X-Cybozu-API-Token": api_token},
                    params={
                        "app": app_id,
                        "lang": "en",
                        "query": query,
                    },
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
