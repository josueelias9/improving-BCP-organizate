"""
User repository implementation - Framework layer
"""
import uuid
from typing import Optional, List
from sqlmodel import Session
from models import User, UserCreate, UserUpdate
from src.Capplication.repositories import IUserRepository
import crud


class UserRepository(IUserRepository):
    """SQLModel implementation of User repository - delegates to crud.py"""
    
    def create_user(self, session: Session, user_create: UserCreate) -> User:
        """Create a new user"""
        return crud.create_user(session, user_create)
    
    def get_user(self, session: Session, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return crud.get_user(session, user_id)
    
    def get_user_by_email(self, session: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return crud.get_user_by_email(session, email)
    
    def get_all_users(self, session: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return crud.get_all_users(session, skip, limit)
    
    def update_user(self, session: Session, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
        """Update user"""
        return crud.update_user(session, user_id, user_update)
    
    def delete_user(self, session: Session, user_id: uuid.UUID) -> bool:
        """Delete user"""
        return crud.delete_user(session, user_id)
    
    def user_exists(self, session: Session, email: str) -> bool:
        """Check if user exists by email"""
        return crud.user_exists(session, email)