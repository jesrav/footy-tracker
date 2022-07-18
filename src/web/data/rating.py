import datetime
import sqlalchemy as sa

from src.web.data.modelbase import SqlAlchemyBase


class Rating(SqlAlchemyBase):
    __tablename__ = 'ratings'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user: int = sa.Column(sa.Integer)
    last_match_used_for_calculation: int = sa.Column(sa.Integer)
    created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
