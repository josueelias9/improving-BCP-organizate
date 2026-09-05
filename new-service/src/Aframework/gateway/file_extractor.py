"""
File System Gateway Implementation - Framework Layer
Concrete implementation of file system operations
"""

import logging
from pathlib import Path
import os

from src.Capplication.gateway.file_extractor import IFileExtractorGateway

logger = logging.getLogger(__name__)


class FileExtractorGateway(IFileExtractorGateway):
    """
    - this class arises from the need to have a gateway that handles file system operations in a consistent manner across the application. It abstracts the underlying file system operations, allowing for easier testing and maintenance.
    - this class is responsible for file system operations, such as saving files and checking if a file exists.
    - it should also be able to read files that are sent throulgh the API, which are stored in a temporary folder, and then deleted after processing or files located in a remote bucket like S3
    """

    def save_file(self, filename: str, content: str, output_dir: str) -> str:
        try:
            dir_path = Path(output_dir)
            dir_path.mkdir(parents=True, exist_ok=True)

            file_path = dir_path / filename

            with open(file_path, "w", encoding="utf-8", newline="") as f:
                f.write(content)

            logger.info(f"Successfully saved file: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise IOError(f"Failed to save file: {str(e)}")

    def file_exists(self, filepath: str) -> bool:
        return os.path.exists(filepath)

    def list_subdirectories(self, directory: str) -> list[str]:
        return [str(p) for p in Path(directory).iterdir() if p.is_dir()]

    def list_files(self, directory: str, extension: str) -> list[str]:
        ext = extension.lower()
        return [
            str(p)
            for p in Path(directory).iterdir()
            if p.is_file() and p.suffix.lower() == ext
        ]
