import uuid

from src.Capplication.gateway.db import IDocumentDbGateway


class DeleteDocumentUseCase:
    def __init__(self, document_gateway: IDocumentDbGateway):
        self.document_gateway = document_gateway

    def execute(self, document_id: uuid.UUID) -> None:
        """Delete document by ID"""
        self.document_gateway.delete(document_id)
