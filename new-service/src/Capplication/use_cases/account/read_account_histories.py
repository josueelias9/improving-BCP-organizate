from src.Capplication.DTO.account_dto import DTOGetAccountHistoriesResponse, DTOHistory
from src.Capplication.gateway.db import IHistoryDbGateway


class ReadAccountHistoriesUseCase:
    def __init__(self, history_gateway: IHistoryDbGateway):
        self.history_gateway = history_gateway

    def execute(self, account_id: str) -> DTOGetAccountHistoriesResponse:
        histories = self.history_gateway.get_by_account_id(account_id)
        return DTOGetAccountHistoriesResponse(
            histories=[
                DTOHistory(
                    id=h.id,
                    account_id=h.account_id,
                    balance=h.balance,
                    registration_date=h.registration_date,
                )
                for h in histories
            ],
            total_count=len(histories),
        )
