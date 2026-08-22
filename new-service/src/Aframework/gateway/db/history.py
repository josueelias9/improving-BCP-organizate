"""
History Gateway - Interface Adapter Layer
Implements history persistence operations
"""

import logging
from sqlmodel import Session, select

from models import History as HistoryModel
from src.Denterprise.entities import HistoryEntity
from src.Capplication.gateway.db import IHistoryDbGateway

logger = logging.getLogger(__name__)


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

        logger.info(
            f"History created for account {history.account_id}: balance={history.balance}"
        )
        return HistoryEntity(
            id=db_history.id,
            account_id=db_history.account_id,
            balance=db_history.balance,
            registration_date=db_history.registration_date,
        )

    def get_by_account_id(self, account_id: str) -> list[HistoryEntity]:
        """Return all history snapshots for an account."""
        statement = (
            select(HistoryModel)
            .where(HistoryModel.account_id == account_id)
            .order_by(HistoryModel.registration_date.asc())
        )
        histories = self.session.exec(statement).all()

        return [
            HistoryEntity(
                id=h.id,
                account_id=h.account_id,
                balance=h.balance,
                registration_date=h.registration_date,
            )
            for h in histories
        ]
