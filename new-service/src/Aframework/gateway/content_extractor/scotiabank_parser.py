import json
import logging
import os
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import List, Optional

import requests

from src.Capplication.gateway.content_extractor import IStatementParser
from src.Denterprise.entities import TransactionEntity
from src.Aframework.gateway.content_extractor.utils import read_binary_file

logger = logging.getLogger(__name__)


class ScotiabankParser(IStatementParser):
    """Parser for Scotiabank screenshots captured from the mobile app."""

    @property
    def file_extension(self) -> str:
        return ".jpeg"

    def read_file(self, filepath: str) -> str:
        image_path = Path(filepath)
        if not image_path.exists():
            raise FileNotFoundError(f"Image '{filepath}' not found")

        image_bytes = read_binary_file(str(image_path))
        text = self._read_with_tesseract(image_path, image_bytes)
        return text.strip()

    def _read_with_tesseract(self, image_path: Path, image_bytes: bytes) -> str:
        service_url = os.getenv("TESSERACT_SERVICE_URL")
        if service_url:
            try:
                options = {
                    "languages": ["spa", "eng"],
                    "pageSegmentationMethod": 6,
                    "ocrEngineMode": 1,
                    "dpi": 300,
                }
                response = requests.post(
                    f"{service_url.rstrip('/')}/tesseract",
                    files={"file": (image_path.name, image_bytes, "image/jpeg")},
                    data={"options": json.dumps(options)},
                    timeout=60,
                )
                response.raise_for_status()
                payload = response.json()
                stdout = payload.get("data", {}).get("stdout", "")
                if stdout:
                    return stdout
            except Exception as exc:
                logger.warning(
                    "Tesseract HTTP OCR failed for %s: %s. Falling back to local OCR.",
                    image_path,
                    exc,
                )

        try:
            result = subprocess.run(
                [
                    "tesseract",
                    str(image_path),
                    "stdout",
                    "--psm",
                    "6",
                    "-l",
                    "spa+eng",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout
            if result.stderr:
                logger.warning("Local OCR error for %s: %s", image_path, result.stderr)
        except FileNotFoundError:
            logger.warning("Tesseract CLI is not installed for %s", image_path)

        raise ValueError(
            f"Could not OCR image '{image_path}'. Please provide a valid JPEG/PNG screenshot."
        )

    def get_account(self, full_text: str) -> Optional[str]:
        patterns = [
            r"(?:Scotiabank\s*[:\-]?\s*)(\d{3}-\d{7,})",
            r"(?:N[úu]mero\s+de\s+cuenta\s*[:\-]?\s*)(\d{3}-\d{7,})",
            r"(?<!\d)(\d{3}-\d{7,})(?!\d)",
        ]
        for pattern in patterns:
            match = re.search(pattern, full_text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def get_balance(self, full_text: str) -> Optional[float]:
        balance_patterns = [
            r"(?:Saldo\s+disponible|S[/.])\s*[:\-]?\s*([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2})",
            r"S[/.]?\s*([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2})",
            r"([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2})",
        ]

        for pattern in balance_patterns:
            match = re.search(pattern, full_text, flags=re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                normalized = self._normalize_number(value)
                if normalized is not None:
                    return normalized
        return None

    @staticmethod
    def _normalize_number(value: str) -> Optional[float]:
        try:
            cleaned = value.strip().replace(" ", "")
            if not cleaned:
                return None

            if "," in cleaned and "." in cleaned:
                if cleaned.rfind(".") > cleaned.rfind(","):
                    cleaned = cleaned.replace(",", "")
                else:
                    cleaned = cleaned.replace(".", "").replace(",", ".")
            elif "," in cleaned:
                if len(cleaned.split(",")[-1]) == 2:
                    cleaned = cleaned.replace(",", ".")
                else:
                    cleaned = cleaned.replace(",", "")
            elif "." in cleaned:
                if cleaned.count(".") > 1:
                    parts = cleaned.split(".")
                    if len(parts[-1]) == 2:
                        cleaned = "".join(parts[:-1]) + "." + parts[-1]
                    else:
                        cleaned = "".join(parts)

            return float(cleaned)
        except (TypeError, ValueError):
            return None

    def get_initial_day(self, full_text: str) -> Optional[date]:
        return date.today()

    def get_transactions(self, full_text: str) -> List[TransactionEntity]:
        return []
