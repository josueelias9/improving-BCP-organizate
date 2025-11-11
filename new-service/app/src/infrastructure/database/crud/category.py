"""
CRUD operations for Category model
"""
import uuid
from typing import Optional, List
from sqlmodel import Session, select
from models import Category, CategoryCreate, CategoryUpdate


def create_category(session: Session, category_create: CategoryCreate) -> Category:
    """Create a new category"""
    db_category = Category.model_validate(category_create)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def get_category(session: Session, category_id: uuid.UUID) -> Optional[Category]:
    """Get category by ID"""
    return session.get(Category, category_id)


def get_category_by_name(session: Session, category_name: str) -> Optional[Category]:
    """Get category by name"""
    statement = select(Category).where(Category.name == category_name)
    return session.exec(statement).first()


def get_all_categories(session: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get all categories with pagination"""
    statement = select(Category).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_categories_by_parent(session: Session, parent_id: Optional[uuid.UUID], skip: int = 0, limit: int = 100) -> List[Category]:
    """Get categories by parent ID with pagination"""
    if parent_id is None:
        statement = select(Category).where(Category.parent_id.is_(None)).offset(skip).limit(limit)
    else:
        statement = select(Category).where(Category.parent_id == parent_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_root_categories(session: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get root categories (categories with no parent) with pagination"""
    statement = select(Category).where(Category.parent_id.is_(None)).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_category(session: Session, category_id: uuid.UUID, category_update: CategoryUpdate) -> Optional[Category]:
    """Update category"""
    db_category = session.get(Category, category_id)
    if not db_category:
        return None
    
    category_data = category_update.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def delete_category(session: Session, category_id: uuid.UUID) -> bool:
    """Delete category"""
    db_category = session.get(Category, category_id)
    if not db_category:
        return False
    
    session.delete(db_category)
    session.commit()
    return True


def category_exists(session: Session, category_name: str) -> bool:
    """Check if category exists by name"""
    statement = select(Category).where(Category.name == category_name)
    return session.exec(statement).first() is not None