import os

from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    from models.user import User
    from models.rating import UserRating
    from models.ranking import UserRanking
    from models.result import ResultSubmission
    from models.team import Team
    from models.user_stats import UserStats
    SQLModel.metadata.create_all(engine)


# Session dependency
def get_session():
    with Session(engine) as session:
        yield session
