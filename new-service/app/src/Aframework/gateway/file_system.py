"""
File System Gateway Implementation - Framework Layer
Concrete implementation of file system operations
"""

import logging
from pathlib import Path
import os

from src.Capplication.gateway.file_system import IFileSystemGateway

logger = logging.getLogger(__name__)


class FileSystemGateway(IFileSystemGateway):
    """
    - this class arises from the need to have a gateway that handles file system operations in a consistent manner across the application. It abstracts the underlying file system operations, allowing for easier testing and maintenance.
    - this class is responsible for file system operations, such as saving files, checking if a file exists, and reading files in binary mode.
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

    def read_binary_file(self, filepath: str) -> bytes:
        """
        Read a file in binary mode and return its content as bytes.
        The file is always closed before returning.
        """
        if not self.file_exists(filepath):
            raise FileNotFoundError(f"File '{filepath}' not found")

        try:
            with open(filepath, "rb") as f:
                return f.read()

        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            raise IOError(f"Failed to read file: {str(e)}")
