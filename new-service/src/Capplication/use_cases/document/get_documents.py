"""
Get All Documents Use Case - Application Layer

Business logic for retrieving all documents with pagination.
Accepts DTOs at the boundary and works with entities internally.
"""

import logging

from src.Capplication.gateway.db import IDocumentDbGateway, IDocumentFormatDbGateway
from src.Capplication.DTO.document_dto import (
    DTOGetDocumentsResponse,
    DTOGetDocumentsRequest,
    DTODocumentItem,
)

logger = logging.getLogger(__name__)


class GetDocumentsUseCase:
    """
    Use Case: Retrieve all documents with pagination

    Responsibility: Orchestrate document retrieval and conversion to DTO for presentation
    """

    def __init__(
        self,
        document_gateway: IDocumentDbGateway,
        document_format_gateway: IDocumentFormatDbGateway,
    ):
        """
        Initialize use case with required gateways

        Args:
            document_gateway: Gateway for document persistence operations
            document_format_gateway: Gateway for document type operations
        """
        self.document_gateway = document_gateway
        self.document_format_gateway = document_format_gateway

    def execute(self, request: DTOGetDocumentsRequest) -> DTOGetDocumentsResponse:
        """
        Execute the use case to get all documents

        Args:
            request: DTOGetDocumentsRequest with pagination parameters

        Returns:
            DTOGetDocumentsResponse with list of document summaries
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

        # https://pydantic.dev/docs/validation/dev/concepts/models/#nested-attributes
        return DTOGetDocumentsResponse(
            documents=[DTODocumentItem.model_validate(doc) for doc in documents],
            total_returned=len(documents),
            skip=request.skip,
            limit=request.limit,
        )
