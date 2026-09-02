import logging

from src.Capplication.DTO.account_dto import (
    DTOCreateAllAccountHistoriesItemResult,
    DTOCreateAllAccountHistoriesResponse,
)
from src.Capplication.gateway.content_extractor import IStatementParser
from src.Capplication.gateway.db import (
    IAccountDbGateway,
    IDocumentDbGateway,
    IHistoryDbGateway,
)
from src.Capplication.use_cases.account.create_account_history import (
    CreateAccountHistoryUseCase,
)

logger = logging.getLogger(__name__)


class CreateHistoriesUseCase:
    def __init__(
        self,
        account_gateway: IAccountDbGateway,
        history_gateway: IHistoryDbGateway,
        document_gateway: IDocumentDbGateway,
        parsers: dict[str, IStatementParser],
    ):
        self.account_gateway = account_gateway
        self.history_gateway = history_gateway
        self.document_gateway = document_gateway
        self.parsers = parsers

    def execute(self) -> DTOCreateAllAccountHistoriesResponse:
        accounts = self.account_gateway.get_all()

        use_case = CreateAccountHistoryUseCase(
            account_gateway=self.account_gateway,
            history_gateway=self.history_gateway,
            document_gateway=self.document_gateway,
            parsers=self.parsers,
        )

        results: list[DTOCreateAllAccountHistoriesItemResult] = []
        total_histories = 0

        # A failure for one account (e.g. no documents, no new snapshots) must
        # not stop the batch, so each account is processed independently.
        for account in accounts:
            try:
                response = use_case.execute(account_id=account.id)
                total_histories += response.total_count
                results.append(
                    DTOCreateAllAccountHistoriesItemResult(
                        account_id=account.id,
                        success=True,
                        histories=response.histories,
                    )
                )
            except Exception as e:
                logger.warning(
                    f"Could not create histories for account {account.id}: {e}"
                )
                results.append(
                    DTOCreateAllAccountHistoriesItemResult(
                        account_id=account.id,
                        success=False,
                        error=str(e),
                    )
                )

        return DTOCreateAllAccountHistoriesResponse(
            total_accounts=len(accounts),
            total_histories=total_histories,
            results=results,
        )
