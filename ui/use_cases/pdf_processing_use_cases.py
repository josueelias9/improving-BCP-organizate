"""
PDF Processing Use Cases
"""
from domain.repositories import FileRepository, PdfProcessingRepository


class ProcessPdfUseCase:
    """Process uploaded PDF file"""
    
    def __init__(self, file_repo: FileRepository, pdf_processing_repo: PdfProcessingRepository):
        self.file_repo = file_repo
        self.pdf_processing_repo = pdf_processing_repo
    
    def execute(self, doc_type: str = "debit", user_email: str = "admin@bcpextractor.com") -> dict:
        """Execute use case - get file from directory and process it"""
        # Get the file path from the directory
        file_path = self.file_repo.get_single_file_path()
        
        if not file_path:
            raise ValueError("No file found in the directory")
        
        # Process the PDF
        return self.pdf_processing_repo.process_pdf(file_path, doc_type, user_email)
