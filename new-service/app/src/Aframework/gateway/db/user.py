"""User Gateway - Interface Adapter Layer
Implements user persistence operations
Maps between SQLModel User and domain User entity
"""

import logging
from sqlmodel import Session, select
from typing import Optional

from models import User
from src.Denterprise.entities import UserEntity
from src.Capplication.gateway.db import IUserDbGateway

logger = logging.getLogger(__name__)


class UserDbGateway(IUserDbGateway):
    """SQLModel implementation of user gateway"""

    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Get user by email and map to domain entity"""
        statement = select(User).where(User.email == email)
        db_user = self.session.exec(statement).first()

        if not db_user:
            return None

        # Map to domain entity
        return UserEntity(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            is_active=db_user.is_active,
        )

    def create(self, user_data: UserEntity) -> UserEntity:
        """Create a new user and map to domain entity"""
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            is_active=user_data.is_active,
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

        # Map to domain entity
        return UserEntity(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            is_active=db_user.is_active,
        )
