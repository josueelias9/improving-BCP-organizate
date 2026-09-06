"""
Yape Transaction Report Parser - Framework/Adapter Layer
Parses Yape XLSX report format and creates domain entities.

This is an INPUT ADAPTER that:
- Depends on the Yape-specific XLSX layout
- Converts it into clean domain entities
- Belongs in the Interface Adapters layer, NOT the domain layer
"""

import csv
import io
import logging
from datetime import date, datetime
from typing import List, Optional

import openpyxl

from src.Capplication.gateway.content_extractor import IStatementParser
from src.Denterprise.entities import TransactionEntity
from src.Aframework.gateway.content_extractor.utils import read_binary_file

logger = logging.getLogger(__name__)

# Column positions in the "Movimientos" sheet (0-indexed, data starts at row 6)
_COL_TIPO = 0
_COL_ORIGEN = 1
_COL_DESTINO = 2
_COL_MONTO = 3
_COL_MENSAJE = 4
_COL_FECHA = 5

_DATE_FMT = "%d/%m/%Y %H:%M:%S"

# Transaction type mapping: Yape label → domain type
_TIPO_MAP = {
    "PAGASTE": "expense",
    "TE PAGÓ": "income",
}


def _parse_datetime(fecha_str: str) -> Optional[datetime]:
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, _DATE_FMT)
    except ValueError:
        logger.warning(f"Unrecognised date format: {fecha_str}")
        return None


class YapeParser(IStatementParser):
    """Parser for Yape XLSX transaction reports."""

    @property
    def file_extension(self) -> str:
        return ".xlsx"

    def read_file(self, filepath: str) -> str:
        """Read XLSX file and return the raw "Movimientos" rows as CSV text."""
        wb = openpyxl.load_workbook(io.BytesIO(read_binary_file(filepath)))
        ws = wb["Movimientos"]

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["tipo", "origen", "destino", "monto", "mensaje", "fecha"])
        for row in ws.iter_rows(min_row=6, values_only=True):
            if not row[_COL_TIPO]:
                continue
            writer.writerow(
                [
                    row[_COL_TIPO],
                    row[_COL_ORIGEN],
                    row[_COL_DESTINO],
                    row[_COL_MONTO],
                    row[_COL_MENSAJE],
                    row[_COL_FECHA],
                ]
            )
        return buffer.getvalue()

    def get_account(self, full_text: str) -> Optional[str]:
        return "yape"

    def get_balance(self, full_text: str) -> Optional[float]:
        return None

    def get_initial_day(self, full_text: str) -> Optional[date]:
        datetimes = [
            _parse_datetime(r["fecha"])
            for r in csv.DictReader(io.StringIO(full_text))
            if r.get("fecha")
        ]
        valid = [d for d in datetimes if d]
        return min(valid).date() if valid else None

    def get_transactions(self, full_text: str) -> List[TransactionEntity]:
        rows = list(csv.DictReader(io.StringIO(full_text)))
        entities = []
        for idx, row in enumerate(rows):
            tipo = row.get("tipo", "")
            transaction_type = _TIPO_MAP.get(tipo, "expense")

            amount = float(row.get("monto") or 0.0)

            # Use recipient for expenses, sender for income
            if transaction_type == "expense":
                description = row.get("destino") or ""
            else:
                description = row.get("origen") or ""

            # Store the raw message as history when available
            history = row.get("mensaje")

            transaction_date = _parse_datetime(row.get("fecha"))

            entities.append(
                TransactionEntity(
                    order=idx + 1,
                    description=description,
                    history=history,
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_date=transaction_date,
                    currency="SOL",
                )
            )
        return entities
