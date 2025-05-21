import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DuplicateException, SqlException
from app.models.accounts import AccountModel
from app.databases.accounts import account_crud
from app.schemas.accounts import AccountSchema, AccountRiskSchema

logger = logging.getLogger(__name__)

class AccountService:
    def __init__(self):
        self.crud = account_crud

    async def get_all_accounts(self, session: AsyncSession) -> list[AccountSchema]:
        logger.debug("Получение всех аккаунтов")
        accounts = await self.crud.get_all(session=session)
        return accounts

    async def get_account_risk(
        self, account_id: str, session: AsyncSession
    ) -> AccountRiskSchema | None:
        logger.debug(f"Риск для аккаунта {account_id}")
        account = await self.crud.get_risk(
            account_id=account_id, session=session
        )
        return account

    async def create_account(
            self, account_data: AccountSchema, session: AsyncSession
    ) -> None:
        logger.info(f"Создание нового аккаунта: {account_data.account_id}")
        try:
            account = AccountModel(
                account_id=account_data.account_id,
                first_name=account_data.first_name,
                last_name=account_data.last_name,
                middle_name=account_data.middle_name,
                risk=account_data.risk
            )
            await self.crud.add(account=account, session=session)
            logger.info(f"Аккаунт {account_data.account_id} успешно создан")
        except SqlException as exc:
            logger.error(f"Ошибка создания аккаунта: {str(exc)}")
            raise DuplicateException(message=str(exc))

account_service = AccountService()