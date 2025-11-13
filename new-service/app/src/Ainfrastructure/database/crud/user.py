"""
CRUD operations for User model
"""
import uuid
from typing import Optional
from sqlmodel import Session, select
from models import User, UserCreate, UserUpdate


def create_user(session: Session, user_create: UserCreate) -> User:
    """Create a new user"""
    db_user = User.model_validate(user_create)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user(session: Session, user_id: uuid.UUID) -> Optional[User]:
    """Get user by ID"""
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email"""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get users with pagination"""
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_all_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users (alias for get_users)"""
    return get_users(session, skip, limit)


def user_exists(session: Session, email: str) -> bool:
    """Check if user exists by email"""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first() is not None


def update_user(session: Session, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    db_user = session.get(User, user_id)
    if not db_user:
        return None
    
    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(session: Session, user_id: uuid.UUID) -> bool:
    """Delete user"""
    db_user = session.get(User, user_id)
    if not db_user:
        return False
    
    session.delete(db_user)
    session.commit()
    return True