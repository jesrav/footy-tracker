import os

from sqlmodel import SQLModel, create_engine, Session

#DATABASE_URL = "sqlite:///./footy_tracker.db"
DATABASE_URL = os.environ.get("DATABASE_URL")
#DATABASE_USER = os.environ.get("PG_USER")
#DATABASE_PSW = os.environ.get("PG_PSW")
#SQLALCHEMY_DATABASE_URL = "postgresql://footy:9Fockspace@postgresserver/footy"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Session dependency
def get_session():
    with Session(engine) as session:
        yield session
