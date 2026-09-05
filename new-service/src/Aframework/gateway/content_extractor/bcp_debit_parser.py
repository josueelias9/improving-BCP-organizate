"""
BCP Statement Parser - Framework/Adapter Layer
Parses BCP PDF format and creates domain entities

This is an INPUT ADAPTER that:
- Depends on external format (BCP PDF structure)
- Contains parsing logic specific to BCP
- Belongs in the Interface Adapters layer, NOT the domain layer
"""

import re
import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

from src.Capplication.gateway.content_extractor import IStatementParser
from src.Denterprise.entities import TransactionEntity
from src.Aframework.gateway.content_extractor.pdf_utils import extract_pdf_text

logger = logging.getLogger(__name__)


class BCPDebitParser(IStatementParser):
    """
    Parser for BCP bank statements - Interface Adapter

    This class adapts the external BCP PDF format into domain entities.
    It knows about the BCP-specific format but the domain doesn't know about it.
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
        "OCT": "10",
        "NOV": "11",
        "DIC": "12",
        "SET": "09",  # Setiembre
    }

    @property
    def file_extension(self) -> str:
        return ".pdf"

    def read_file(self, file_content: bytes) -> str:
        return extract_pdf_text(file_content)

    def get_account(self, full_text: str) -> Optional[str]:
        """Extract account code from BCP PDF text"""
        account, _ = self._extract_account_code(full_text)
        return account

    def get_balance(self, full_text: str) -> Optional[float]:
        """Extract previous balance from BCP PDF text"""
        return self._extract_saldo_anterior(full_text)

    def get_initial_day(self, full_text: str) -> Optional[date]:
        return self._extract_period(full_text)[0]

    def get_transactions(self, full_text: str) -> List[TransactionEntity]:
        """Parse BCP debit PDF text and return transaction entities."""
        account_code, currency = self._extract_account_code(full_text)
        initial_day, _ = self._extract_period(full_text)
        year = initial_day.year if initial_day else datetime.now().year
        raw_transactions = self._parse_transactions(full_text, year)

        currency_map = {"SOLES": "SOL", "US DOLARES": "USD"}
        currency_code = currency_map.get(currency, "SOL")

        day_counters: dict[date, int] = defaultdict(int)
        entities = []
        for idx, tx in enumerate(raw_transactions):
            cargos = float(tx.get("cargos", 0.0))
            abonos = float(tx.get("abonos", 0.0))
            if cargos == 0.0:
                transaction_type = "income"
                amount = abonos
            else:
                transaction_type = "expense"
                amount = cargos

            fecha_valor = tx.get("fecha_valor")
            if fecha_valor:
                day_counters[fecha_valor] += 1
                transaction_date = datetime.combine(
                    fecha_valor, datetime.min.time()
                ) + timedelta(seconds=day_counters[fecha_valor])
            else:
                transaction_date = None

            entities.append(
                TransactionEntity(
                    order=idx + 1,
                    description=tx.get("description", ""),
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_date=transaction_date,
                    currency=currency_code,
                )
            )
        return entities

    @staticmethod
    def _parse_transactions(text: str, year: int) -> List[dict[str, any]]:
        """
        Parse transactions from BCP PDF text using fixed positions

        This method knows about BCP's specific format and creates domain entities.
        The domain entities don't know they came from BCP format.

        BCP Format (positional):

                  111111111122222222223333333333444444444455555555556666666666777
        0123456789012345678901234567890123456789012345678901234567890123456789012
        ----- ----- ------------------    -       ------------       ------------
          a     b            c            d             e                 f


        a (0-5):   Processing date (5 chars)
        b (6-11):  Value date (5 chars)
        c (12-30): Description (18 chars)
        d (30-31): Internal transaction (1 char)
        e (31-43): Debit/Charge (12 chars)
        f (43-55): Credit/Deposit (12 chars)
        """
        logger.info("Parsing transactions from extracted text...")
        logger.info(f"Extracted text (first 1000 chars): {text[:1000]}")

        transactions = []
        lines = text.split("\n")

        # Pattern to detect lines starting with date (DDMMM)
        date_pattern = r"^\d{2}[A-Z]{3}\s"

        for line_num, line in enumerate(lines):
            # DON'T strip() to preserve positions
            if not line or len(line) < 12:
                continue

            # Check if line starts with date pattern
            if not re.match(date_pattern, line):
                continue

            logger.debug(f"Transaction line found {line_num}: [{line}]")

            try:
                # Extract by fixed positions (BCP-specific format)
                fecha_proceso = line[0:5].strip()  # Position 0-5
                fecha_valor = line[6:11].strip()  # Position 6-11
                description = line[12:30].strip()  # Position 12-30
                internal_transaction = line[
                    34:35
                ].strip()  # Position 30-31 (*, optional)
                egreso_str = line[42:54].strip()  # Position 31-43
                ingreso_str = line[61:].strip()

                # Validate dates have correct format
                if not (len(fecha_proceso) == 5 and len(fecha_valor) == 5):
                    logger.debug(
                        f"Invalid dates in line {line_num}: {fecha_proceso} | {fecha_valor}"
                    )
                    continue

                # Convert dates
                fecha_proceso_formatted = BCPDebitParser._convert_bcp_date(
                    fecha_proceso, year
                )
                fecha_valor_formatted = BCPDebitParser._convert_bcp_date(
                    fecha_valor, year
                )

                # Parse amounts
                egreso = 0.0
                ingreso = 0.0

                if egreso_str:
                    try:
                        egreso = float(egreso_str.replace(",", ""))
                    except ValueError:
                        pass

                if ingreso_str:
                    try:
                        ingreso = float(ingreso_str.replace(",", ""))
                    except ValueError:
                        pass

                # Create domain entity (pure business object)
                transaction = {
                    "fecha_proceso": fecha_proceso_formatted,
                    "fecha_valor": fecha_valor_formatted,
                    "description": description,
                    "cargos": egreso,
                    "abonos": ingreso,
                    "internal_transaction": internal_transaction,
                }

                transactions.append(transaction)

            except Exception as e:
                logger.debug(f"Error parsing line {line_num}: {line} - {str(e)}")
                continue

        logger.info(f"Total transactions found: {len(transactions)}")
        return transactions

    @staticmethod
    def _convert_bcp_date(date_str: str, year: int = 2025) -> Optional[date]:
        """Convert BCP date format DDMMM to Python date object"""
        if not date_str or len(date_str) < 5:
            return None

        try:
            # Extract day and month
            day = int(date_str[:2])
            month_abbr = date_str[2:5].upper()

            if month_abbr in BCPDebitParser.MONTHS_MAP:
                month = int(BCPDebitParser.MONTHS_MAP[month_abbr])
                return date(year, month, day)
            else:
                logger.warning(f"Unrecognized month: {month_abbr}")
                return None

        except Exception as e:
            logger.error(f"Error converting date {date_str}: {str(e)}")
            return None

    @staticmethod
    def _extract_account_code(text: str) -> Optional[tuple[str, str]]:
        """
        Extract account code and currency from BCP PDF text

        Format: _NNN-NNNNNNNN-N-NN__CCCCC

        where:
        - _: space
        - N: digit
        - C: letters (SOLES or DOLARES)

        Example: 191-04106279-0-55  SOLES

        Returns:
            Tuple[str, str]: (account_code, currency) where currency is 'SOLES' or 'DOLARES'
            None if not found
        """
        try:
            lines = text.split("\n")

            # BCP-specific pattern: NNN-NNNNNNNN-N-NN  CURRENCY
            # Example: 191-04106279-0-55  SOLES
            account_pattern = r"\b(\d{3}-\d{8}-\d{1}-\d{2})\s+(SOLES|US DOLARES)"

            for line in lines:
                # Search for BCP account pattern with currency
                match = re.search(account_pattern, line)
                if match:
                    account_code = match.group(1)
                    currency_text = match.group(2)
                    logger.info(
                        f"BCP account code found: {account_code}, Currency: {currency_text}"
                    )
                    return (account_code, currency_text)

            logger.warning(
                "Could not find account code in format NNN-NNNNNNNN-N-NN with currency"
            )
            return None, None

        except Exception as e:
            logger.error(f"Error extracting account code: {str(e)}")
            return None

    @staticmethod
    def _extract_saldo_anterior(text: str) -> Optional[float]:
        """
        Extract previous balance from BCP PDF text

        Format: SALDO ANTERIOR followed by amount at fixed position (column 58-68)
        Example: ------------SALDO ANTERIOR---------------------------------    NNNNNNN.NN
        """
        try:
            lines = text.split("\n")

            for line in lines:
                # Search for line containing "SALDO ANTERIOR"
                if "SALDO ANTERIOR" in line:
                    # Extract amount from position 58 onwards
                    saldo_str = line[58:].strip()

                    if saldo_str:
                        try:
                            saldo = float(saldo_str.replace(",", ""))
                            logger.info(f"Previous balance found: {saldo}")
                            return saldo
                        except ValueError:
                            logger.warning(
                                f"Could not convert previous balance to number: {saldo_str}"
                            )

            logger.warning("No line with SALDO ANTERIOR found")
            return None

        except Exception as e:
            logger.error(f"Error extracting previous balance: {str(e)}")
            return None

    @staticmethod
    def _extract_period(text: str) -> Tuple[Optional[date], Optional[date]]:
        """
        Extract statement period from BCP PDF text

        Format: DEL  NN/NN/NN  AL  NN/NN/NN
        Example: DEL  01/10/25  AL  31/10/25

        Returns:
            tuple: (initial_day, final_day) as date objects or (None, None) if not found
        """
        try:
            lines = text.split("\n")

            # Pattern: DEL  NN/NN/NN  AL  NN/NN/NN
            period_pattern = (
                r"DEL\s+(\d{2})/(\d{2})/(\d{2})\s+AL\s+(\d{2})/(\d{2})/(\d{2})"
            )

            for line in lines:
                match = re.search(period_pattern, line.upper())
                if match:
                    # Convert dates from DD/MM/YY to date objects
                    day1, month1, year1 = (
                        int(match.group(1)),
                        int(match.group(2)),
                        int(match.group(3)),
                    )
                    day2, month2, year2 = (
                        int(match.group(4)),
                        int(match.group(5)),
                        int(match.group(6)),
                    )

                    # Assume 2000+ if year < 50, else 1900+
                    year1 = 2000 + year1 if year1 < 50 else 1900 + year1
                    year2 = 2000 + year2 if year2 < 50 else 1900 + year2

                    initial_day = date(year1, month1, day1)
                    final_day = date(year2, month2, day2)

                    logger.info(f"Period found: FROM {initial_day} TO {final_day}")
                    return (initial_day, final_day)

            logger.warning("No line with pattern DEL NN/NN/NN AL NN/NN/NN found")
            return (None, None)

        except Exception as e:
            logger.error(f"Error extracting period: {str(e)}")
            return (None, None)
