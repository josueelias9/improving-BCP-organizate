"""Category Gateway - Interface Adapter Layer
Implements category persistence operations
Maps between SQLModel Category and domain Category entity
"""

import logging
from sqlmodel import Session, select
from typing import Optional, List

from models import Category as CategoryModel
from src.Denterprise.entities import CategoryEntity
from src.Capplication.gateway.db import ICategoryDbGateway

logger = logging.getLogger(__name__)


class CategoryDbGateway(ICategoryDbGateway):
    """SQLModel implementation of category gateway"""

    def __init__(self, session: Session):
        self.session = session

    def get_by_name(self, name: str) -> Optional[CategoryEntity]:
        """
        Get category by name (case-insensitive)

        Args:
            name: Name of the category to search for

        Returns:
            Domain Category entity if found, None otherwise
        """
        statement = select(CategoryModel).where(CategoryModel.name.ilike(name))
        db_category = self.session.exec(statement).first()

        if not db_category:
            return None

        # Map to domain entity
        category = CategoryEntity()
        category.name = db_category.name
        category.description = db_category.description
        return category

    def get_all(self) -> List[CategoryEntity]:
        """
        Get all categories

        Returns:
            List of domain Category entities
        """
        statement = select(CategoryModel)
        db_categories = self.session.exec(statement).all()

        # Map to domain entities
        categories = []
        for db_cat in db_categories:
            category = CategoryEntity()
            category.name = db_cat.name
            category.description = db_cat.description
            categories.append(category)

        return categories
