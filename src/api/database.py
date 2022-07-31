from sqlmodel import SQLModel, create_engine, Session
from schemas import User, Team, ResultSubmission, UserRating
DATABASE_URL = "sqlite:///./footy_tracker_sqlmodel.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Session dependency
def get_session():
    with Session(engine) as session:
        yield session
