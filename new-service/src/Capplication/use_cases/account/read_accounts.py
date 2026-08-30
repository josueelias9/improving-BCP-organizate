import os

from src.Capplication.DTO.account_dto import DTOAccount, DTOReadAccountsResponse
from src.Capplication.gateway.db import IAccountDbGateway


class ReadAccountsUseCase:
    def __init__(self, account_gateway: IAccountDbGateway):
        self.account_gateway = account_gateway

    def execute(self) -> DTOReadAccountsResponse:
        entities = self.account_gateway.get_all()
        base_url = os.getenv("BACKEND_URL")
        accounts = [
            DTOAccount(
                id=e.id,
                links=[
                    {
                        "rel": "transactions",
                        "href": f"{base_url}/accounts/{e.id}/transactions",
                        "action": "POST",
                    },
                    {
                        "rel": "transactions",
                        "href": f"{base_url}/accounts/{e.id}/transactions",
                        "action": "GET",
                    },
                    {
                        "rel": "histories",
                        "href": f"{base_url}/accounts/{e.id}/histories",
                        "action": "POST",
                    },
                    {
                        "rel": "histories",
                        "href": f"{base_url}/accounts/{e.id}/histories",
                        "action": "GET",
                    },
                ],
            )
            for e in entities
        ]
        return DTOReadAccountsResponse(accounts=accounts, total_count=len(accounts))
