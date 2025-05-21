# app/services/transactions.py
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DuplicateException, SqlException
from app.models.transactions import TransactionModel
from app.databases.transactions import transaction_crud
from app.schemas.transactions import TransactionCreateSchema, TransactionSchema

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self):
        self.crud = transaction_crud

    async def get_all_payments(self, session: AsyncSession) -> list[TransactionSchema]:
        logger.debug("Получение всех транзакций")
        payments = await self.crud.get_all(session=session)
        return payments

    async def get_transaction_by_transaction_id(
        self, transaction_id: str, session: AsyncSession
    ) -> TransactionSchema | None:
        logger.debug(f"Получение транзакции по ID: {transaction_id}")
        transaction = await self.crud.get_transaction(
            transaction_id=transaction_id, session=session
        )
        return transaction

    async def create_transaction(
            self, transaction_data: TransactionCreateSchema, session: AsyncSession
    ) -> None:
        logger.info("Создание новой транзакции")
        try:
            transaction = TransactionModel(
                sender_account_id=transaction_data.sender_account_id,
                receiver_account_id=transaction_data.receiver_account_id,
                transaction_amount=transaction_data.transaction_amount,
                transaction_type=transaction_data.transaction_type,
                timestamp=transaction_data.timestamp,
                transaction_status=transaction_data.transaction_status,
                fraud_flag=transaction_data.fraud_flag,
                geolocation=transaction_data.geolocation,
                device_user=transaction_data.device_user
            )
            await self.crud.add(transaction=transaction, session=session)
            logger.info(f"Транзакция {transaction.id} успешно создана")
        except SqlException as exc:
            logger.error(f"Ошибка создания транзакции: {str(exc)}")
            raise DuplicateException(message=str(exc))

transaction_service = TransactionService()