"""
File Use Cases
"""
from domain.repositories import FileRepository


class SaveFileUseCase:
    """Save uploaded file"""
    
    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo
    
    def execute(self, file_content: bytes, filename: str) -> str:
        """Execute use case"""
        return self.file_repo.save_file(file_content, filename)
