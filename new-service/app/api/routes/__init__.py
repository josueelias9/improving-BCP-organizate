"""
Routes module for API endpoints
"""

from . import health
from . import document
from . import transaction
from . import category

__all__ = ["health", "document", "transaction", "category"]
