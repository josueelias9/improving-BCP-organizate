"""
BCP Credit Statement Parser - Framework/Adapter Layer
Parses BCP Credit Card PDF format and creates domain entities

This is an INPUT ADAPTER that:
- Depends on external format (BCP Credit Card PDF structure)
- Contains parsing logic specific to BCP Credit Cards
- Creates clean domain entities
- Belongs in the Interface Adapters layer, NOT the domain layer
"""

import re
import logging
from datetime import date, datetime
from typing import List, Optional, Dict, Any

from src.Capplication.gateway.content_extractor import IStatementParser
from src.Denterprise.entities import TransactionEntity
from src.Aframework.gateway.content_extractor.pdf_utils import extract_pdf_text

logger = logging.getLogger(__name__)


class BCPCreditParser(IStatementParser):
    """
    Parser for BCP credit card statements - Interface Adapter

    This class adapts the external BCP credit card PDF format into domain entities.
    """

    # BCP-specific month mapping (Spanish to numeric)
    MONTHS_MAP = {
        "ENE": "01",
        "FEB": "02",
        "MAR": "03",
        "ABR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AGO": "08",
        "SEP": "09",
        "SET": "09",  # Setiembre
        "OCT": "10",
        "NOV": "11",
        "DIC": "12",
    }

    @property
    def file_extension(self) -> str:
        return ".pdf"

    def read_file(self, file_content: bytes) -> str:
        return extract_pdf_text(file_content)

    def get_account(self, full_text: str) -> Optional[str]:
        pass

    def get_balance(self, full_text: str) -> Optional[float]:
        pass

    def get_initial_day(self, full_text: str) -> Optional[date]:

        # Extract date range
        date_range_match = re.search(
            r"Del\s+(\d{2})/(\d{2})/(\d{4})\s+al\s+(\d{2})/(\d{2})/(\d{4})",
            full_text,
        )

        if date_range_match:
            day1, month1, year1 = (
                int(date_range_match.group(1)),
                int(date_range_match.group(2)),
                int(date_range_match.group(3)),
            )

            start_date = date(year1, month1, day1)

            return start_date
        return None

    def get_transactions(self, full_text: str) -> List[TransactionEntity]:
        """Parse BCP credit card PDF text and return transaction entities."""
        try:
            currency_match = re.search(r"Moneda:\s+([A-Z]{3})", full_text)
            currency_raw = currency_match.group(1) if currency_match else "PEN"

            currency_map = {"PEN": "SOL", "USD": "USD", "EUR": "EUR"}
            currency_code = currency_map.get(currency_raw, "SOL")

            raw_transactions = self.parse_transactions(full_text)

            entities = []
            for idx, tx in enumerate(raw_transactions):
                fecha_valor_str = tx.get("fecha_valor")
                transaction_date = (
                    datetime.combine(
                        date.fromisoformat(fecha_valor_str), datetime.min.time()
                    )
                    if fecha_valor_str
                    else None
                )
                cargos = float(tx.get("cargos", 0.0))
                abonos = float(tx.get("abonos", 0.0))
                if cargos == 0.0:
                    transaction_type = "income"
                    amount = abonos
                else:
                    transaction_type = "expense"
                    amount = cargos
                entities.append(
                    TransactionEntity(
                        order=idx + 1,
                        description=tx.get("description", ""),
                        history=tx.get("history"),
                        amount=amount,
                        transaction_type=transaction_type,
                        transaction_date=transaction_date,
                        currency=currency_code,
                    )
                )
            return entities

        except Exception as e:
            logger.error(f"Error parsing BCP credit PDF: {e}")
            raise

    @staticmethod
    def extract_saldo_anterior(text: str) -> tuple[float, float]:
        """
        Extract previous balance for soles and dollars

        Format: SALDO ANTERIOR    11,852.58      267.89
        Returns: (soles, dolares)
        """
        try:
            # Pattern to match "SALDO ANTERIOR" followed by two amounts
            pattern = r"SALDO\s+ANTERIOR\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)"
            match = re.search(pattern, text)

            if match:
                soles_str = match.group(1).replace(",", "")
                dolares_str = match.group(2).replace(",", "")

                soles = float(soles_str) if soles_str else 0.0
                dolares = float(dolares_str) if dolares_str else 0.0

                logger.info(
                    f"Extracted previous balance - Soles: {soles}, Dolares: {dolares}"
                )
                return soles, dolares
            else:
                logger.warning("Could not find SALDO ANTERIOR in text")
                return 0.0, 0.0

        except Exception as e:
            logger.error(f"Error extracting saldo anterior: {e}")
            return 0.0, 0.0

    def parse_transactions(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse credit card transactions from BCP PDF text

        Format:
        11Set    10Set    IZI*MINIMARKET EDU     LIMA          PE                CONSUMO          9.20
        DDDDD    DDDDD    AAAAAAAAAAAAAAAAAA     BBBB          PP                CCCCCCC       MMMMMMM

        Where:
        - D: dates (transaction date, process date)
        - A: description
        - B: city
        - P: country
        - C: transaction type
        - M: amount
        """
        logger.info("Parsing credit card transactions from extracted text...")

        transactions = []
        lines = text.split("\n")

        # Pattern to detect transaction lines (starting with date format DDMMM)
        date_pattern = r"^\s*\d{1,2}[A-Za-z]{3}\s+"

        for line_num, line in enumerate(lines):
            if not line or len(line) < 30:
                continue

            # Check if line starts with date pattern
            if not re.match(date_pattern, line):
                continue

            logger.debug(f"Credit transaction line found {line_num}: [{line}]")

            try:
                # Parse the line using regex to extract fields
                # Pattern: date1 date2 description city country type amount
                pattern = r"^\s*(\d{1,2}[A-Za-z]{3})\s+(\d{1,2}[A-Za-z]{3})\s+(.{20,}?)\s+([A-Z\s]{4,20})\s+([A-Z]{2})\s+([A-Z\s]+?)\s+([\d,]+\.?\d*)\s*$"

                match = re.match(pattern, line)

                if match:
                    fecha_transaccion_str = match.group(1).strip()
                    fecha_proceso_str = match.group(2).strip()
                    description = match.group(3).strip()
                    city = match.group(4).strip()
                    country = match.group(5).strip()
                    transaction_type = match.group(6).strip()
                    amount_str = match.group(7).strip()

                    # Convert dates
                    fecha_transaccion = self._convert_bcp_date(fecha_transaccion_str)
                    fecha_proceso = self._convert_bcp_date(fecha_proceso_str)

                    # Parse amount
                    amount = float(amount_str.replace(",", ""))

                    transaction = {
                        "fecha_valor": (
                            fecha_transaccion.isoformat() if fecha_transaccion else None
                        ),
                        "fecha_proceso": (
                            fecha_proceso.isoformat() if fecha_proceso else None
                        ),
                        "description": description,
                        "city": city,
                        "country": country,
                        "transaction_type": transaction_type,
                        "cargos": amount,
                        "abonos": 0.0,
                        "history": f"{city}, {country}",
                    }

                    transactions.append(transaction)
                    logger.debug(f"Valid credit transaction: {transaction}")
                else:
                    logger.debug(f"Line did not match pattern: {line}")

            except Exception as e:
                logger.debug(f"Error parsing credit line {line_num}: {line} - {str(e)}")
                continue

        logger.info(f"Total credit transactions found: {len(transactions)}")
        return transactions

    def _convert_bcp_date(self, date_str: str) -> Optional[date]:
        """Convert BCP date format DDMMM to Python date object"""
        if not date_str or len(date_str) < 4:
            return None

        try:
            # Extract day and month
            # Handle formats like "11Set" or "1Set"
            match = re.match(r"(\d{1,2})([A-Za-z]{3})", date_str)
            if not match:
                return None

            day = int(match.group(1))
            month_abbr = match.group(2).upper()

            if month_abbr in self.MONTHS_MAP:
                month = int(self.MONTHS_MAP[month_abbr])
                # Assume current year (2025 based on example)
                year = 2025
                return date(year, month, day)
            else:
                logger.warning(f"Unrecognized month: {month_abbr}")
                return None

        except Exception as e:
            logger.error(f"Error converting date {date_str}: {e}")
            return None
