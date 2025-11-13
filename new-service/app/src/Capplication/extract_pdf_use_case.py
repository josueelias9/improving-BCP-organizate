from typing import BinaryIO
from ..Ddomain.entities import ExtractionResult
from ..Ddomain.repositories import PDFExtractorRepository


class ExtractPDFUseCase:
    """Use case for extracting transactions from PDF"""
    
    def __init__(self, pdf_extractor: PDFExtractorRepository):
        self._pdf_extractor = pdf_extractor
    
    def execute(self, pdf_file: BinaryIO, filename: str) -> ExtractionResult:
        """Execute PDF extraction"""
        return self._pdf_extractor.extract_transactions(pdf_file, filename)