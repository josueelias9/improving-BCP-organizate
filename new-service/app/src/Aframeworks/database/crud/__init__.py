"""
Database CRUD operations - Framework layer
Only exports Repository classes for Clean Architecture
All CRUD functions are now in app/crud.py
"""

from .user import UserRepository
from .document import DocumentRepository

__all__ = [
    "UserRepository",
    "DocumentRepository",
]