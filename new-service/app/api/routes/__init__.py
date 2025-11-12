"""
Routes module for API endpoints
"""

from . import health
from . import pdf_processing 
from . import pdf_upload
from . import output_files

__all__ = ["health", "pdf_processing", "pdf_upload", "output_files"]