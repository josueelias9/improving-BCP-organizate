"""
Import Transactions from CSV Use Case - Application Layer
Orchestrates the flow of importing and updating transactions from CSV file
"""

import logging
import csv
from pathlib import Path
from typing import Optional, List

from src.Capplication.DTO.transaction_dto import (
    DTOImportTransactionsFromCsvResponse,
    DTOImportTransactionsFromCsvRequest,
)
from src.Capplication.gateway.db import ITransactionDbGateway, ICategoryDbGateway

logger = logging.getLogger(__name__)


class ImportTransactionsFromCsvUseCase:
    """Use case for importing and updating transactions from CSV file"""

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
        category_gateway: ICategoryDbGateway,
    ):
        """
        Initialize use case with gateway dependencies

        Args:
            transaction_gateway: Transaction gateway interface
            category_gateway: Category gateway interface
        """
        self.transaction_gateway = transaction_gateway
        self.category_gateway = category_gateway

    def execute(
        self, dto_request: DTOImportTransactionsFromCsvRequest
    ) -> DTOImportTransactionsFromCsvResponse:
        """
        Execute the use case: import and update transactions from CSV

        Args:
            dto_request: DTO containing optional specific CSV filename

        Returns:
            ImportTransactionsResult with operation summary
        """
        try:
            # 1. Find the CSV file
            csv_path = self._find_csv_file(dto_request.csv_filename)

            if not csv_path.exists():
                return DTOImportTransactionsFromCsvResponse(
                    success=False,
                    updated_count=0,
                    skipped_count=0,
                    errors=[f"CSV file not found: {csv_path}"],
                    total_rows=0,
                    message="CSV file not found",
                )

            # 2. Read and parse CSV
            rows = self._read_csv(csv_path)

            if not rows:
                return DTOImportTransactionsFromCsvResponse(
                    success=False,
                    updated_count=0,
                    skipped_count=0,
                    errors=["CSV file is empty or has no data rows"],
                    total_rows=0,
                    message="CSV file is empty",
                )

            # 3. Update transactions
            updated_count = 0
            skipped_count = 0
            errors = []

            for idx, row in enumerate(
                rows, start=2
            ):  # Start at 2 because row 1 is header
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

            success = updated_count > 0
            message = f"Successfully updated {updated_count}/{len(rows)} transactions"

            logger.info(message)

            return DTOImportTransactionsFromCsvResponse(
                success=success,
                updated_count=updated_count,
                skipped_count=skipped_count,
                errors=errors if errors else [],
                total_rows=len(rows),
                message=message,
            )

        except Exception as e:
            logger.error(f"Unexpected error during import: {str(e)}")
            return DTOImportTransactionsFromCsvResponse(
                success=False,
                updated_count=0,
                skipped_count=0,
                errors=[f"Internal error: {str(e)}"],
                total_rows=0,
                message=f"Import failed: {str(e)}",
            )

    def _find_csv_file(self, filename: Optional[str] = None) -> Path:
        """
        Find the CSV file in the /downloads/output directory

        Args:
            filename: Optional specific filename, otherwise uses latest

        Returns:
            Path to the CSV file
        """
        output_dir = Path("/downloads/output")

        if filename:
            return output_dir / filename

        # Find the most recent transactions CSV file
        csv_files = list(output_dir.glob("transactions*.csv"))

        if not csv_files:
            raise ValueError(
                "No transaction CSV files found in /downloads/output directory"
            )

        # Sort by modification time, newest first
        csv_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        return csv_files[0]

    def _read_csv(self, csv_path: Path) -> List[dict]:
        """
        Read and parse CSV file

        Args:
            csv_path: Path to CSV file

        Returns:
            List of row dictionaries
        """
        rows = []

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Validate required columns
            if "unique_identifier" not in reader.fieldnames:
                raise ValueError("CSV must contain 'unique_identifier' column")

            for row in reader:
                rows.append(row)

        return rows

    def _update_transaction_from_row(self, row: dict) -> bool:
        """
        Update a transaction from a CSV row

        Args:
            row: Dictionary with CSV row data

        Returns:
            True if updated, False if transaction not found
        """
        unique_identifier = row.get("unique_identifier", "").strip()

        if not unique_identifier:
            raise ValueError("unique_identifier is required")

        # Get transaction by unique_identifier
        transaction = self.transaction_gateway.get_by_unique_identifier(
            unique_identifier
        )

        if not transaction:
            return False

        # Prepare update data
        update_data = {}

        # Update history if provided
        history = row.get("history", "").strip()
        if history:
            update_data["history"] = history

        # Update category if provided
        category_name = row.get("category_name", "").strip()
        if category_name:
            category = self.category_gateway.get_by_name(category_name)
            if category:
                update_data["category_id"] = category.id
            else:
                logger.warning(f"Category not found: {category_name}")

        # Update transaction if there's data to update
        if update_data:
            return self.transaction_gateway.update(transaction.id, update_data)

        return False
