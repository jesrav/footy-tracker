from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
