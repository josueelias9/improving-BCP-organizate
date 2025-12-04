"""
Category Gateway - Interface Adapter Layer
Implements category persistence operations
"""
import logging
from sqlmodel import Session, select
from typing import Optional, List

from models import Category
from src.Capplication.interfaces.db import ICategoryDbGateway

logger = logging.getLogger(__name__)


class CategoryDbGateway(ICategoryDbGateway):
    """SQLModel implementation of category gateway"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """
        Get category by name (case-insensitive)
        
        Args:
            name: Name of the category to search for
            
        Returns:
            Category if found, None otherwise
        """
        statement = select(Category).where(Category.name.ilike(name))
        return self.session.exec(statement).first()
    
    def get_all(self) -> List[Category]:
        """
        Get all categories
        
        Returns:
            List of all categories
        """
        statement = select(Category)
        return self.session.exec(statement).all()
