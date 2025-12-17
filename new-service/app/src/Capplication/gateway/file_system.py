"""
File System Gateway Interface - Application Layer
Defines contracts for file system operations
"""

from abc import ABC, abstractmethod
from pathlib import Path


class IFileSystemGateway(ABC):
    """Interface for file system operations"""

    @abstractmethod
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
        pass
