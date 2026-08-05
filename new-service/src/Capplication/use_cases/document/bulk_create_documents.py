"""
Bulk Create Documents Use Case - Application Layer
Iterates over document type folders and creates all documents found
"""

import logging
from pathlib import Path

from src.Capplication.DTO.document_dto import (
    DTOBulkCreateDocumentsRequest,
    DTOBulkCreateDocumentsResponse,
    DTOBulkCreateDocumentItemResult,
    DTOCreateDocumentRequest,
)
from src.Capplication.gateway.db import IDocumentDbGateway, IUserDbGateway
from src.Capplication.gateway.content_extractor import IStatementParser
from src.Capplication.gateway.file_extractor import IFileExtractorGateway
from src.Aframework.gateway.db.document_format import IDocumentTypeDbGateway
from src.Capplication.use_cases.document.create_document import CreateDocumentUseCase

logger = logging.getLogger(__name__)


class BulkCreateDocumentsUseCase:
    """Scans subfolders of base_directory; each subfolder name is treated as document_format."""

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        user_gateway: IUserDbGateway,
        document_type_gateway: IDocumentTypeDbGateway,
        file_extractor_gateway: IFileExtractorGateway,
        parsers: dict[str, IStatementParser],
    ):
        self.document_gateway = document_gateway
        self.user_gateway = user_gateway
        self.document_type_gateway = document_type_gateway
        self.file_extractor_gateway = file_extractor_gateway
        self.parsers = parsers

    def execute(self, request: DTOBulkCreateDocumentsRequest) -> DTOBulkCreateDocumentsResponse:
        results: list[DTOBulkCreateDocumentItemResult] = []
        created = already_existed = failed = 0

        subdirs = self.file_extractor_gateway.list_subdirectories(request.base_directory)

        for subdir in subdirs:
            document_format = Path(subdir).name
            parser = self.parsers.get(document_format)

            if parser is None:
                logger.warning(f"No parser registered for document type '{document_format}', skipping folder")
                continue

            pdf_files = self.file_extractor_gateway.list_files(subdir, ".pdf")

            for pdf_filepath in pdf_files:
                item = self._process_single(pdf_filepath, document_format, request.user_email, parser)
                results.append(item)
                if item.success and not item.already_exists:
                    created += 1
                elif item.success and item.already_exists:
                    already_existed += 1
                else:
                    failed += 1

        return DTOBulkCreateDocumentsResponse(
            total=len(results),
            created=created,
            already_existed=already_existed,
            failed=failed,
            results=results,
        )

    def _process_single(
        self, pdf_filepath: str, document_format: str, user_email: str, parser: IStatementParser
    ) -> DTOBulkCreateDocumentItemResult:
        try:
            use_case = CreateDocumentUseCase(
                document_gateway=self.document_gateway,
                user_gateway=self.user_gateway,
                document_type_gateway=self.document_type_gateway,
                file_extractor_gateway=self.file_extractor_gateway,
                parser_gateway=parser,
            )
            response = use_case.execute(DTOCreateDocumentRequest(pdf_filepath=pdf_filepath, user_email=user_email))
            return DTOBulkCreateDocumentItemResult(
                pdf_filepath=pdf_filepath,
                document_format=document_format,
                success=response.success,
                document_id=response.document_id,
                already_exists=response.already_exists,
                transactions_count=response.transactions_count,
            )
        except Exception as e:
            logger.error(f"Failed to process '{pdf_filepath}': {e}")
            return DTOBulkCreateDocumentItemResult(
                pdf_filepath=pdf_filepath,
                document_format=document_format,
                success=False,
                error=str(e),
            )
