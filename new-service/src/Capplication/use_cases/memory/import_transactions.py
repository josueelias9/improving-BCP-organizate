"""
Import Transactions from CSV Use Case - Application Layer
Orchestrates the flow of importing and updating transactions from CSV file
"""

import logging
import csv
from pathlib import Path
from typing import List

from src.Capplication.DTO.memory_dto import (
    DTOImportTransactionsResponse,
    DTOImportTransactionsRequest,
)
from src.Capplication.gateway.db import (
    ITransactionDbGateway,
    ICategoryDbGateway,
)

logger = logging.getLogger(__name__)


class ImportTransactionsUseCase:
    """Use case for importing and updating transactions from CSV file"""

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
        category_gateway: ICategoryDbGateway,
    ):
        self.transaction_gateway = transaction_gateway
        self.category_gateway = category_gateway

    def execute(
        self, dto_request: DTOImportTransactionsRequest
    ) -> DTOImportTransactionsResponse:
        try:
            account_id = dto_request.account_id
            filename = f"transactions__{account_id}"
            csv_path = Path(f"/workspace/files/exports/{filename}.csv")

            if not csv_path.exists():
                return DTOImportTransactionsResponse(
                    success=False,
                    updated_count=0,
                    skipped_count=0,
                    errors=[f"CSV file not found: {csv_path}"],
                    total_rows=0,
                    message="CSV file not found",
                )

            rows = self._read_csv(csv_path)

            if not rows:
                return DTOImportTransactionsResponse(
                    success=False,
                    updated_count=0,
                    skipped_count=0,
                    errors=["CSV file is empty or has no data rows"],
                    total_rows=0,
                    message="CSV file is empty",
                )

            updated_count = 0
            skipped_count = 0
            errors = []

            for idx, row in enumerate(rows, start=2):
                try:
                    result = self._update_transaction_from_row(row)
                    if result:
                        updated_count += 1
                    else:
                        skipped_count += 1
                        errors.append(
                            f"Row {idx}: Transaction not updated: {row.get('unique_identifier', 'N/A')}"
                        )
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"Row {idx}: {str(e)}")
                    logger.error(f"Error processing row {idx}: {str(e)}")

            message = f"Successfully updated {updated_count}/{len(rows)} transactions"
            logger.info(message)

            return DTOImportTransactionsResponse(
                success=updated_count > 0,
                updated_count=updated_count,
                skipped_count=skipped_count,
                errors=errors,
                total_rows=len(rows),
                message=message,
            )

        except Exception as e:
            logger.error(f"Unexpected error during import: {str(e)}")
            return DTOImportTransactionsResponse(
                success=False,
                updated_count=0,
                skipped_count=0,
                errors=[f"Internal error: {str(e)}"],
                total_rows=0,
                message=f"Import failed: {str(e)}",
            )

    def _read_csv(self, csv_path: Path) -> List[dict]:
        rows = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "unique_identifier" not in reader.fieldnames:
                raise ValueError("CSV must contain 'unique_identifier' column")
            for row in reader:
                rows.append(row)
        return rows

    def _update_transaction_from_row(self, row: dict) -> bool:
        unique_identifier = row.get("unique_identifier", "").strip()
        if not unique_identifier:
            raise ValueError("unique_identifier is required")

        transaction = self.transaction_gateway.get_by_unique_identifier(
            unique_identifier
        )
        if not transaction:
            return False

        update_data = {}

        history = row.get("history", "").strip()
        if history:
            update_data["history"] = history

        category_name = row.get("category_name", "").strip()
        if category_name:
            category = self.category_gateway.get_by_name(category_name)
            if category:
                update_data["category_id"] = category.id
            else:
                logger.warning(f"Category not found: {category_name}")

        if update_data:
            return self.transaction_gateway.update(transaction.id, update_data)

        return False
