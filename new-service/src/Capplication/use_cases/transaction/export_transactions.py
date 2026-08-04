"""
Export Transactions Use Case - Application Layer
Orchestrates the flow of exporting transactions to CSV format
"""

import logging
import csv
import io
from typing import List
from datetime import datetime

from src.Capplication.DTO.transaction_dto import (
    DTOExportTransactionsRequest,
    DTOExportTransactionsResponse,
)
from src.Capplication.gateway.db import ITransactionDbGateway, IDocumentDbGateway
from src.Capplication.gateway.file_extractor import IFileExtractorGateway

logger = logging.getLogger(__name__)


class ExportTransactionsUseCase:
    """Use case for exporting transactions to CSV format"""

    def __init__(
        self,
        transaction_gateway: ITransactionDbGateway,
        file_extractor_gateway: IFileExtractorGateway,
        document_gateway: IDocumentDbGateway,
    ):
        self.transaction_gateway = transaction_gateway
        self.file_extractor_gateway = file_extractor_gateway
        self.document_gateway = document_gateway

    def execute(
        self, filters: DTOExportTransactionsRequest
    ) -> DTOExportTransactionsResponse:
        """
        Execute the use case: export transactions to CSV

        Args:
            filters: Filter criteria for export

        Returns:
            ExportTransactionsResult with CSV content and metadata

        Raises:
            ValueError: If filters are invalid or no data found
        """
        try:
            # 1. Validate month format if provided
            if filters.month:
                self._validate_month_format(filters.month)

            # 2. Retrieve transactions from gateway
            transactions = self.transaction_gateway.get_all_filtered(
                month=filters.month, document_id=filters.document_id
            )

            if not transactions:
                raise ValueError("No transactions found with the specified filters")

            # 3. Generate CSV content
            csv_content = self._generate_csv(transactions)

            # 4. Generate filename
            doc = self.document_gateway.get_by_id(filters.document_id)
            filename = f"{doc.unique_identifier}.csv"

            # 5. Save file using file system gateway
            file_path = self.file_extractor_gateway.save_file(
                filename=filename, content=csv_content, output_dir="/workspace/files/exports/"
            )

            logger.info(
                f"Successfully exported {len(transactions)} transactions to CSV: {file_path}"
            )

            return DTOExportTransactionsResponse(
                success=True,
                csv_content=csv_content,
                filename=filename,
                transaction_count=len(transactions),
                file_path=file_path,
                month=filters.month,
                document_id=filters.document_id,
            )

        except ValueError as e:
            logger.error(f"Export validation error: {str(e)}")
            return DTOExportTransactionsResponse(
                success=False,
                csv_content="",
                filename="",
                transaction_count=0,
                error_message=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error during export: {str(e)}")
            return DTOExportTransactionsResponse(
                success=False,
                csv_content="",
                filename="",
                transaction_count=0,
                error_message=f"Internal error: {str(e)}",
            )

    def _validate_month_format(self, month: str) -> None:
        """
        Validate month format is YYYY-MM

        Args:
            month: Month string to validate

        Raises:
            ValueError: If format is invalid
        """
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise ValueError("Invalid month format. Use YYYY-MM (e.g., 2025-01)")

    def _generate_csv(self, transactions: List[dict]) -> str:
        """
        Generate CSV content from transactions
        Only includes transactions that have category_name or history data

        Args:
            transactions: List of transaction dictionaries

        Returns:
            CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header - only the 3 required fields
        headers = ["category_name", "unique_identifier", "history"]
        writer.writerow(headers)

        # Write data rows - only transactions with category_name or history
        for transaction in transactions:
            category_name = transaction.get("category_name", "") or ""
            history = transaction.get("history", "") or ""

            # Only include if category_name or history has data
            if category_name.strip() or history.strip():
                writer.writerow(
                    [category_name, transaction.get("unique_identifier", ""), history]
                )

        return output.getvalue()
