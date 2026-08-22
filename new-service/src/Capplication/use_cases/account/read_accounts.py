from src.Capplication.gateway.db import IAccountDbGateway
from src.Capplication.DTO.account_dto import DTOGetAccountsResponse, DTOAccount


class ReadAccountsUseCase:

    def __init__(self, account_gateway: IAccountDbGateway):
        self.account_gateway = account_gateway

    def execute(self) -> DTOGetAccountsResponse:
        entities = self.account_gateway.get_all()
        accounts = [
            DTOAccount(
                id=e.id,
                links=[
                    {
                        "rel": "self",
                        "href": f"/accounts/{e.id}",
                        "action":"GET",
                    },
                    {
                        "rel": "transactions",
                        "href": f"/accounts/{e.id}/transactions",
                        "action":"GET",
                    },
                    {
                        "rel": "histories",
                        "href": f"/accounts/{e.id}/histories",
                        "action":"GET",
                    },
                ],
            )
            for e in entities
        ]
        return DTOGetAccountsResponse(accounts=accounts, total_count=len(accounts))
