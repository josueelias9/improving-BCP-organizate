from src.Capplication.gateway.db import IAccountDbGateway
from src.Capplication.DTO.account_dto import DTOReadAccountsResponse, DTOAccount


class ReadAccountsUseCase:

    def __init__(self, account_gateway: IAccountDbGateway):
        self.account_gateway = account_gateway

    # TODO: maybe we can have a single DTO
    def execute(self) -> DTOReadAccountsResponse:
        entities = self.account_gateway.get_all()
        accounts = [
            DTOAccount(
                id=e.id,
                links=[
                    {
                        "rel": "self",
                        "href": f"http://localhost:8000/accounts/{e.id}",
                        "action": "GET",
                    },
                    {
                        "rel": "transactions",
                        "href": f"http://localhost:8000/accounts/{e.id}/transactions",
                        "action": "GET",
                    },
                    {
                        "rel": "histories",
                        "href": f"http://localhost:8000/accounts/{e.id}/histories",
                        "action": "GET",
                    },
                    {
                        "rel": "transactions",
                        "href": f"http://localhost:8000/accounts/{e.id}/transactions",
                        "action": "POST",
                    },
                ],
            )
            for e in entities
        ]
        return DTOReadAccountsResponse(accounts=accounts, total_count=len(accounts))
