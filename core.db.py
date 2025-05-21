# app/core/db.py
import logging
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.base_model import BaseInit
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    url=settings.db.url,
    echo=True
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    logger.debug("Создание новой сессии базы")
    async with async_session_maker() as session:
        yield session

async def create_tables():
    logger.info("Проверка таблиц базы")
    async with engine.begin() as conn:
        inspector = await conn.run_sync(lambda conn: inspect(conn))
        existing_tables = await conn.run_sync(lambda _: inspector.get_table_names())
        needed_tables = BaseInit.metadata.tables.keys()
        tables_to_create = [table for table in needed_tables if table not in existing_tables]

        if tables_to_create:
            logger.info(f"Создание недостающих таблиц: {tables_to_create}")
            await conn.run_sync(
                lambda conn: BaseInit.metadata.create_all(
                    conn,
                    tables=[BaseInit.metadata.tables[table] for table in tables_to_create]
                )
            )
        else:
            logger.debug("Таблицы уже существуют")