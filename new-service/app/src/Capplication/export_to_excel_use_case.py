from typing import BinaryIO
from ..Ddomain.entities import ExtractionResult
from ..Ddomain.repositories import PDFExtractorRepository, ExcelGeneratorRepository


class ExportToExcelUseCase:
    """Use case for exporting PDF transactions to Excel"""
    
    def __init__(self, pdf_extractor: PDFExtractorRepository, excel_generator: ExcelGeneratorRepository):
        self._pdf_extractor = pdf_extractor
        self._excel_generator = excel_generator
    
    def execute(self, pdf_file: BinaryIO, filename: str) -> BinaryIO:
        """Execute PDF extraction and Excel generation"""
        # Extract transactions from PDF
        extraction_result = self._pdf_extractor.extract_transactions(pdf_file, filename)
        
        if not extraction_result.success:
            raise Exception(extraction_result.error_message or "PDF extraction failed")
        
        if not extraction_result.has_transactions:
            raise Exception("No transaction data found in PDF")
        
        # Generate Excel file
        return self._excel_generator.generate_excel(extraction_result.transactions, filename)