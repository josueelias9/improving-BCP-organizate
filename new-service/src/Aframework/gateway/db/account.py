"""
Account and History Gateways - Interface Adapter Layer
Implements account and history persistence operations
"""

import logging
from datetime import date
from sqlmodel import Session

from models import Account as AccountModel, History as HistoryModel
from src.Denterprise.entities import AccountEntity, HistoryEntity
from src.Capplication.gateway.db import IAccountDbGateway, IHistoryDbGateway

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


class HistoryDbGateway(IHistoryDbGateway):
    """SQLModel implementation of history gateway"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, history: HistoryEntity) -> HistoryEntity:
        """Create a new history record (balance snapshot)"""
        db_history = HistoryModel(
            account_id=history.account_id,
            balance=history.balance,
            registration_date=history.registration_date,
        )
        self.session.add(db_history)
        self.session.commit()
        self.session.refresh(db_history)

        logger.info(f"History created for account {history.account_id}: balance={history.balance}")
        return HistoryEntity(
            id=db_history.id,
            account_id=db_history.account_id,
            balance=db_history.balance,
            registration_date=db_history.registration_date,
        )
