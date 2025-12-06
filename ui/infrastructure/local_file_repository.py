"""
Local File System Implementation of File Repository
"""
import os
import shutil
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
            # Check if directory has files and clear it
            if os.path.exists(self.base_dir) and os.listdir(self.base_dir):
                logger.info(f"Clearing directory: {self.base_dir}")
                for item in os.listdir(self.base_dir):
                    item_path = os.path.join(self.base_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            
            # Save the new file
            file_path = os.path.join(self.base_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
