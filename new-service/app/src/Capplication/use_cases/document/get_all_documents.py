"""
Get All Documents Use Case - Application Layer

Business logic for retrieving all documents with pagination.
Accepts DTOs at the boundary and works with entities internally.
"""

import logging
from typing import List
from dataclasses import dataclass

from src.Capplication.gateway.db import IDocumentDbGateway
from src.Capplication.DTO.document_dto import (
    DTOGetAllDocumentsResponse,
    GetAllDocumentsRequest
)
from src.Capplication.DTO.other_dto import DTODocumentSummary


logger = logging.getLogger(__name__)




class GetAllDocumentsUseCase:
    """
    Use Case: Retrieve all documents with pagination

    Responsibility: Orchestrate document retrieval and conversion to DTO for presentation
    """

    def __init__(self, document_gateway: IDocumentDbGateway):
        """
        Initialize use case with required gateway

        Args:
            document_gateway: Gateway for document persistence operations
        """
        self.document_gateway = document_gateway

    def execute(self, request: GetAllDocumentsRequest) -> DTOGetAllDocumentsResponse:
        """
        Execute the use case to get all documents

        Args:
            request: GetAllDocumentsRequest with pagination parameters

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


        # Convert entities to DTOs for presentation
        document_summaries: List[DTODocumentSummary] = []

        for doc_entity in documents:
            # Extract metadata from document entity
            summary = DTODocumentSummary(
                id=str(doc_entity.id),
                currency=doc_entity.currency,
                unique_identifier=doc_entity.unique_identifier,
                processed=doc_entity.processed,
                user_id=str(doc_entity.user_id),
                document_type_id=str(doc_entity.document_type_id),
                transactions_count=len(doc_entity.data) if doc_entity.data else 0,
            )
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
