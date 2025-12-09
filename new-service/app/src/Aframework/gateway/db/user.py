"""User Gateway - Interface Adapter Layer
Implements user persistence operations
Maps between SQLModel User and domain User entity
"""

import logging
from sqlmodel import Session, select
from typing import Optional

from models import User as UserModel, UserCreate
from src.Denterprise.entities import UserEntity
from src.Capplication.interfaces.db import IUserDbGateway

logger = logging.getLogger(__name__)


class UserDbGateway(IUserDbGateway):
    """SQLModel implementation of user gateway"""

    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Get user by email and map to domain entity"""
        statement = select(UserModel).where(UserModel.email == email)
        db_user = self.session.exec(statement).first()

        if not db_user:
            return None

        # Map to domain entity
        user = UserEntity()
        user.email = db_user.email
        user.name = db_user.name
        user.is_active = db_user.is_active
        user.customer_type = db_user.customer_type

        return user

    def create(self, user_create: UserCreate) -> UserEntity:
        """Create a new user and map to domain entity"""
        db_user = UserModel.model_validate(user_create)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

        # Map to domain entity
        user = UserEntity()
        user.email = db_user.email
        user.name = db_user.name
        user.is_active = db_user.is_active
        user.customer_type = db_user.customer_type

        return user
