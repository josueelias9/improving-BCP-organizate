"""
Account Gateway - Interface Adapter Layer
Implements account persistence operations
"""

import logging
from sqlmodel import Session, select

from models import Account as AccountModel
from src.Denterprise.entities import AccountEntity
from src.Capplication.gateway.db import IAccountDbGateway

logger = logging.getLogger(__name__)


class AccountDbGateway(IAccountDbGateway):
    """SQLModel implementation of account gateway"""

    def __init__(self, session: Session):
        self.session = session

    def get_or_create(self, account_id: str) -> tuple[AccountEntity, bool]:
        """Return existing account or create a new one"""
        db_account = self.session.get(AccountModel, account_id)

        if db_account:
            return AccountEntity(id=db_account.id), False

        db_account = AccountModel(id=account_id)
        self.session.add(db_account)
        self.session.commit()
        self.session.refresh(db_account)

        logger.info(f"Account created: {account_id}")
        return AccountEntity(id=db_account.id), True

    def get_all(self) -> list[AccountEntity]:
        """Return all accounts"""
        accounts = self.session.exec(select(AccountModel)).all()
        return [AccountEntity(id=a.id) for a in accounts]
