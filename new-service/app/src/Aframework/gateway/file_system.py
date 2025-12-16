"""
File System Gateway Implementation - Framework Layer
Concrete implementation of file system operations
"""

import logging
from pathlib import Path
from src.Capplication.gateway.file_system import IFileSystemGateway

logger = logging.getLogger(__name__)


class FileSystemGateway(IFileSystemGateway):
    """Concrete implementation of file system gateway"""

    def save_file(self, filename: str, content: str, output_dir: str) -> str:
        """
        Save content to a file in the specified directory

        Args:
            filename: Name of the file to save
            content: Content to write to the file
            output_dir: Directory where to save the file

        Returns:
            Full path of the saved file as string

        Raises:
            IOError: If file cannot be saved
        """
        try:
            # Create output directory if it doesn't exist
            dir_path = Path(output_dir)
            dir_path.mkdir(parents=True, exist_ok=True)

            # Build full file path
            file_path = dir_path / filename

            # Write content to file
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                f.write(content)

            logger.info(f"Successfully saved file: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise IOError(f"Failed to save file: {str(e)}")
