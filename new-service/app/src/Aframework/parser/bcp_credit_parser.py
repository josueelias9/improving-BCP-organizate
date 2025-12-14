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
from datetime import date
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class BCPCreditParser:
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

    def get_data(self, full_text: str) -> tuple[dict[str, Any], str, str]:
        """Parse BCP credit card PDF text and extract transaction data"""
        try:
            # Extract account code
            account_code_match = re.search(r"Cuenta:\s+(\d{20})", full_text)
            account_code = account_code_match.group(1) if account_code_match else ""

            # Extract date range
            date_range_match = re.search(
                r"Del\s+(\d{2}/\d{2}/\d{4})\s+al\s+(\d{2}/\d{2}/\d{4})", full_text
            )
            initial_day = date_range_match.group(1) if date_range_match else ""
            final_day = date_range_match.group(2) if date_range_match else ""

            # Extract currency
            currency_match = re.search(r"Moneda:\s+([A-Z]{3})", full_text)
            currency = currency_match.group(1) if currency_match else "PEN"

            # Extract previous balance (saldo anterior) for soles and dollars
            saldo_anterior_soles, saldo_anterior_dolares = self.extract_saldo_anterior(
                full_text
            )

            # Extract transactions
            transactions = self.parse_transactions(full_text)

            data = {
                "account_code": account_code,
                "initial_day": initial_day,
                "final_day": final_day,
                "currency": currency,
                "saldo_anterior_soles": saldo_anterior_soles,
                "saldo_anterior_dolares": saldo_anterior_dolares,
                "transactions": transactions,
            }

            return (
                data,
                currency,
                f"{account_code}__{initial_day}__{final_day}__{saldo_anterior_soles}",
            )

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
                    fecha_transaccion = self.convert_bcp_date(fecha_transaccion_str)
                    fecha_proceso = self.convert_bcp_date(fecha_proceso_str)

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

    def convert_bcp_date(self, date_str: str) -> Optional[date]:
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
