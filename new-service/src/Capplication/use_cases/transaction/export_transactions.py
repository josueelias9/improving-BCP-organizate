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

            # 2. Retrieve transactions from gateway
            document_id = filters.document_id
            transactions = self.transaction_gateway.get_by_document_id(
                document_id=document_id
            )

            if not transactions:
                raise ValueError("No transactions found with the specified filters")

            # 3. Generate CSV content
            csv_content = self._generate_csv(transactions)

            # 4. Generate filename
            doc = self.document_gateway.get_by_id(document_id)
            filename = f"{doc.document_format_name}__{doc.registration_date}__{doc.id}.csv"

            # 5. Save file using file system gateway
            file_path = self.file_extractor_gateway.save_file(
                filename=filename,
                content=csv_content,
                output_dir="/workspace/files/exports/",
            )

            logger.info(
                f"Successfully exported {len(transactions)} transactions to CSV: {file_path}"
            )

            return DTOExportTransactionsResponse(
                success=True,
                filename=filename,
                transaction_count=len(transactions),
                file_path=file_path,
                document_id=filters.document_id,
            )

        except ValueError as e:
            logger.error(f"Export validation error: {str(e)}")
            return DTOExportTransactionsResponse(
                success=False,
                filename="",
                transaction_count=0,
                error_message=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error during export: {str(e)}")
            return DTOExportTransactionsResponse(
                success=False,
                filename="",
                transaction_count=0,
                error_message=f"Internal error: {str(e)}",
            )

    # TODO: i think this should go in the file driver gateway, but for now it's here
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
        headers = [
            "category_name",
            "unique_identifier",
            "history",
        ]
        writer.writerow(headers)

        # Write data rows - only transactions with category_name or history
        for transaction in transactions:

            category_name = transaction.category_name or ""
            unique_identifier = transaction.unique_identifier or ""
            history = transaction.history or ""

            writer.writerow([category_name, unique_identifier, history])

        return output.getvalue()
