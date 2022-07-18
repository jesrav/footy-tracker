import datetime
import sqlalchemy as sa

from src.web.data.modelbase import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nickname: str = sa.Column(sa.String, unique=True, nullable=False)
    email: str = sa.Column(sa.String, index=True, unique=True, nullable=False)
    hash_password: str = sa.Column(sa.String, nullable=False)
    created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
    last_login: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)

