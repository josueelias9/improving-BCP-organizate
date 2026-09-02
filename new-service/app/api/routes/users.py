"""
User routes - HTTP Interface
Handles user-scoped operations, including bulk document import.
"""

import logging

from fastapi import APIRouter, HTTPException

from api.deps import SessionDep
from src.Aframework.gateway.db.account import AccountDbGateway
from src.Aframework.gateway.db.document import DocumentDbGateway
from src.Aframework.gateway.db.document_format import DocumentFormatDbGateway
from src.Aframework.gateway.db.user import UserDbGateway
from src.Aframework.gateway.file_extractor import FileExtractorGateway
from src.Aframework.gateway.content_extractor.bcp_credit_parser import BCPCreditParser
from src.Aframework.gateway.content_extractor.bcp_debit_parser import BCPDebitParser
from src.Aframework.gateway.content_extractor.yape_parser import YapeParser
from src.Capplication.use_cases.users.bulk_create_documents import (
    BulkCreateDocumentsUseCase,
    DTOBulkCreateDocumentsRequest,
    DTOBulkCreateDocumentsResponse,
)

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.post("/{user_id}/documents", response_model=DTOBulkCreateDocumentsResponse)
async def create_user_documents(
    user_id: str,
    dto_request: DTOBulkCreateDocumentsRequest,
    session: SessionDep,
):
    """
    Scan base_directory subfolders and create documents for the given user.
    Each subfolder name is used as the document type.
    """
    try:
        parsers = {
            "bcp_credit": BCPCreditParser(),
            "bcp_debit": BCPDebitParser(),
            "yape": YapeParser(),
        }
        use_case = BulkCreateDocumentsUseCase(
            document_gateway=DocumentDbGateway(session),
            user_gateway=UserDbGateway(session),
            document_format_gateway=DocumentFormatDbGateway(session),
            file_extractor_gateway=FileExtractorGateway(),
            parsers=parsers,
            account_gateway=AccountDbGateway(session),
            user_id=user_id,
        )
        return use_case.execute(dto_request)
    except Exception as e:
        logger.error(f"Error in bulk document creation for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Bulk creation failed for user {user_id}: {str(e)}",
        )
