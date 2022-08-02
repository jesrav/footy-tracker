from sqlmodel import SQLModel, create_engine, Session
from models.result import ResultSubmission
from models.team import Team
from models.rating import UserRating
from models.user import User

DATABASE_URL = "sqlite:///./footy_tracker.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Session dependency
def get_session():
    with Session(engine) as session:
        yield session
