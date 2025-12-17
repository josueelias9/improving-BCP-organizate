"""
Get All Documents Use Case - Application Layer

Business logic for retrieving all documents with pagination.
Accepts DTOs at the boundary and works with entities internally.
"""

import logging
from typing import List

from src.Capplication.gateway.db import IDocumentDbGateway, IDocumentTypeDbGateway
from src.Capplication.DTO.document_dto import (
    DTOGetAllDocumentsResponse,
    DTOGetAllDocumentsRequest,
)


logger = logging.getLogger(__name__)


class GetAllDocumentsUseCase:
    """
    Use Case: Retrieve all documents with pagination

    Responsibility: Orchestrate document retrieval and conversion to DTO for presentation
    """

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        document_type_gateway: IDocumentTypeDbGateway,
    ):
        """
        Initialize use case with required gateways

        Args:
            document_gateway: Gateway for document persistence operations
            document_type_gateway: Gateway for document type operations
        """
        self.document_gateway = document_gateway
        self.document_type_gateway = document_type_gateway

    def execute(self, request: DTOGetAllDocumentsRequest) -> DTOGetAllDocumentsResponse:
        """
        Execute the use case to get all documents

        Args:
            request: DTOGetAllDocumentsRequest with pagination parameters

        Returns:
            DTOGetAllDocumentsResponse with list of document summaries
        """
        # Validate pagination parameters
        if request.skip < 0:
            raise ValueError("Skip value must be non-negative")

        if request.limit < 1 or request.limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")

        # Get all documents as entities from gateway
        documents = self.document_gateway.get_all_as_entities(
            skip=request.skip, limit=request.limit
        )

        # Get all document types to map names
        document_types = self.document_type_gateway.get_all()
        document_type_map = {str(dt.id): dt.name for dt in document_types}

        # Convert entities to dicts for presentation
        document_summaries: List[dict] = []

        for doc_entity in documents:
            # Extract metadata from document entity
            summary = {
                "id": str(doc_entity.id),
                "currency": doc_entity.currency,
                "unique_identifier": doc_entity.unique_identifier,
                "processed": doc_entity.processed,
                "user_id": str(doc_entity.user_id),
                "document_type_id": str(doc_entity.document_type_id),
                "document_type_name": document_type_map.get(
                    str(doc_entity.document_type_id), "Unknown"
                ),
                "transactions_count": len(doc_entity.data) if doc_entity.data else 0,
            }
            document_summaries.append(summary)

        logger.info(
            f"Retrieved {len(document_summaries)} documents "
            f"(skip={request.skip}, limit={request.limit})"
        )

        # Return DTO response
        return DTOGetAllDocumentsResponse(
            documents=document_summaries,
            total_returned=len(document_summaries),
            skip=request.skip,
            limit=request.limit,
        )
