"""
Local File System Implementation of File Repository
"""
import os
import logging
from domain.repositories import FileRepository

logger = logging.getLogger(__name__)


class LocalFileRepository(FileRepository):
    """File repository using local file system"""
    
    def __init__(self, base_dir: str = "/shared_files/only_one_file"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file to local directory"""
        try:
            file_path = os.path.join(self.base_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
