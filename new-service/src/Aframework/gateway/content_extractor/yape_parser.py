"""
Yape Transaction Report Parser - Framework/Adapter Layer
Parses Yape XLSX report format and creates domain entities.

This is an INPUT ADAPTER that:
- Depends on the Yape-specific XLSX layout
- Converts it into clean domain entities
- Belongs in the Interface Adapters layer, NOT the domain layer
"""

import io
import json
import logging
from datetime import date, datetime
from typing import List, Optional

import openpyxl

from src.Capplication.gateway.content_extractor import IStatementParser
from src.Denterprise.entities import TransactionEntity

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


def _parse_date(fecha_str: str) -> Optional[date]:
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, _DATE_FMT).date()
    except ValueError:
        logger.warning(f"Unrecognised date format: {fecha_str}")
        return None


class YapeParser(IStatementParser):
    """Parser for Yape XLSX transaction reports."""

    @property
    def file_extension(self) -> str:
        return ".xlsx"

    def read_file(self, file_content: bytes) -> str:
        """Read XLSX bytes and return a JSON string of transaction rows."""
        wb = openpyxl.load_workbook(io.BytesIO(file_content))
        ws = wb["Movimientos"]

        rows = []
        for row in ws.iter_rows(min_row=6, values_only=True):
            if not row[_COL_TIPO]:
                continue
            rows.append(
                {
                    "tipo": row[_COL_TIPO],
                    "origen": row[_COL_ORIGEN],
                    "destino": row[_COL_DESTINO],
                    "monto": row[_COL_MONTO],
                    "mensaje": row[_COL_MENSAJE],
                    "fecha": row[_COL_FECHA],
                }
            )
        return json.dumps(rows, ensure_ascii=False)

    def get_account(self, full_text: str) -> Optional[str]:
        return "yape"

    def get_balance(self, full_text: str) -> Optional[float]:
        return None

    def get_initial_day(self, full_text: str) -> Optional[date]:
        dates = [_parse_date(r["fecha"]) for r in json.loads(full_text) if r.get("fecha")]
        valid = [d for d in dates if d]
        return min(valid) if valid else None

    def get_final_day(self, full_text: str) -> Optional[date]:
        dates = [_parse_date(r["fecha"]) for r in json.loads(full_text) if r.get("fecha")]
        valid = [d for d in dates if d]
        return max(valid) if valid else None

    def get_transactions(self, full_text: str) -> List[TransactionEntity]:
        rows = json.loads(full_text)
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

            transaction_date = _parse_date(row.get("fecha"))

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
