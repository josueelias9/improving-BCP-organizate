"""
Get All Document Types Use Case - Application Layer

Business logic for retrieving all document types.
Accepts DTOs at the boundary and works with entities internally.
"""

import logging
from typing import List, Dict, Any

from src.Capplication.gateway.db import IDocumentFormatDbGateway
from src.Capplication.DTO.document_format_dto import DTOReadDocumentFormatsResponse

logger = logging.getLogger(__name__)


class ReadDocumentFormatsUseCase:
    """
    Use Case: Retrieve all document types

    Responsibility: Orchestrate document type retrieval and conversion to DTO for presentation
    """

    def __init__(self, document_format_gateway: IDocumentFormatDbGateway):
        """
        Initialize use case with required gateway

        Args:
            document_format_gateway: Gateway for document type persistence operations
        """
        self.document_format_gateway = document_format_gateway

    def execute(self) -> DTOReadDocumentFormatsResponse:
        """
        Execute the use case to get all document types

        Returns:
            DTOReadDocumentFormatsResponse with list of document type dicts
        """
        # Get all document types as entities from gateway
        document_type_entities = self.document_format_gateway.get_all()

        # Convert entities to simple dicts for presentation
        document_types: List[Dict[str, Any]] = []

        for doc_type_entity in document_type_entities:
            doc_type_dict = {
                "id": str(doc_type_entity.id),
                "name": doc_type_entity.name,
            }
            document_types.append(doc_type_dict)

        logger.info(f"Retrieved {len(document_types)} document types")

        # Return DTO response
        return DTOReadDocumentFormatsResponse(
            document_types=document_types, total_count=len(document_types)
        )
