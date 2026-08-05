"""
File System Gateway Interface - Application Layer
Defines contracts for file system operations
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class IFileExtractorGateway(ABC):
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

    @abstractmethod
    def file_exists(self, filepath: str) -> bool:
        """
        Check if a file exists

        Args:
            filepath: Path to the file to check

        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def read_binary_file(self, filepath: str) -> bytes:
        """
        Read a file in binary mode and return its content as bytes.
        The file is always closed before returning.

        Args:
            filepath: Path to the file to read

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
        """
        pass

    @abstractmethod
    def list_subdirectories(self, directory: str) -> List[str]:
        """Return full paths of immediate subdirectories inside directory."""
        pass

    @abstractmethod
    def list_files(self, directory: str, extension: str) -> List[str]:
        """Return full paths of files matching extension (case-insensitive) inside directory."""
        pass
