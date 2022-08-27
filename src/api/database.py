import os

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)


async def create_db_and_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

#
# def create_db_and_tables():
#     from models.user import User
#     from models.rating import UserRating
#     from models.ranking import UserRanking
#     from models.result import ResultSubmission
#     from models.team import Team
#     from models.user_stats import UserStats
#     SQLModel.metadata.create_all(engine)
#
#
# # Session dependency
# def get_session():
#     with Session(engine) as session:
#         yield session
