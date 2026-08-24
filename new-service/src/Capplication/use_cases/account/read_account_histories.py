from src.Capplication.DTO.account_dto import DTOReadAccountHistoriesResponse, DTOHistory
from src.Capplication.gateway.db import IHistoryDbGateway


class ReadAccountHistoriesUseCase:
    def __init__(self, history_gateway: IHistoryDbGateway):
        self.history_gateway = history_gateway

    def execute(self, account_id: str) -> DTOReadAccountHistoriesResponse:
        histories = self.history_gateway.get_by_account_id(account_id)
        return DTOReadAccountHistoriesResponse(
            histories=[DTOHistory.model_validate(h) for h in histories],
            total_count=len(histories),
        )
