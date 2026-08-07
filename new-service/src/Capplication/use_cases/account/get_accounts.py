from src.Capplication.gateway.db import IAccountDbGateway
from src.Capplication.DTO.account_dto import DTOGetAccountsResponse, DTOAccount


class GetAccountsUseCase:

    def __init__(self, account_gateway: IAccountDbGateway):
        self.account_gateway = account_gateway

    def execute(self) -> DTOGetAccountsResponse:
        entities = self.account_gateway.get_all()
        accounts = [DTOAccount(id=e.id) for e in entities]
        return DTOGetAccountsResponse(accounts=accounts, total_count=len(accounts))
