from sqlmodel import SQLModel, create_engine
from schemas import User, Team, ResultSubmission, UserRating
DATABASE_URL = "sqlite:///./footy_tracker_sqlmodel.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)
