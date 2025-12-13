"""
BCP Statement Parser - Framework/Adapter Layer
Parses BCP PDF format and creates domain entities

This is an INPUT ADAPTER that:
- Depends on external format (BCP PDF structure)
- Contains parsing logic specific to BCP
- Creates clean domain entities (BCPTransactionEntity)
- Belongs in the Interface Adapters layer, NOT the domain layer
"""

import re
import logging
logger = logging.getLogger(__name__)


class BCPCreditParser:
    def get_data(self, full_text: str) -> dict:
        """Parse BCP credit PDF text and extract transaction data"""
        try:
            # Extract account code
            account_code_match = re.search(r"Cuenta:\s+(\d{20})", full_text)
            account_code = account_code_match.group(1) if account_code_match else ""

            # Extract date range
            date_range_match = re.search(r"Del\s+(\d{2}/\d{2}/\d{4})\s+al\s+(\d{2}/\d{2}/\d{4})", full_text)
            initial_day = date_range_match.group(1) if date_range_match else ""
            final_day = date_range_match.group(2) if date_range_match else ""

            # Extract currency
            currency_match = re.search(r"Moneda:\s+([A-Z]{3})", full_text)
            currency = currency_match.group(1) if currency_match else ""

            # Extract transactions
            transactions = self._extract_transactions(full_text)

            return {
                "account_code": account_code,
                "initial_day": initial_day,
                "final_day": final_day,
                "currency": currency,
                "transactions": transactions,
            }
        except Exception as e:
            logger.error(f"Error parsing BCP credit PDF: {e}")
            raise