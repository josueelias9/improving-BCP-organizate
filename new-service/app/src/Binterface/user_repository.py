"""
User Repository - Interface Adapter Layer
Implements user persistence operations
"""
import uuid
import logging
from sqlmodel import Session, select
from typing import Optional

from models import User, UserCreate

logger = logging.getLogger(__name__)


class UserRepository:
    """SQLModel implementation of user repository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def create(self, user_create: UserCreate) -> User:
        """Create a new user"""
        db_user = User.model_validate(user_create)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
