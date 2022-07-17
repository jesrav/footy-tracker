import datetime
import sqlalchemy as sa
from sqlalchemy import ForeignKey

from data.modelbase import SqlAlchemyBase


class Match(SqlAlchemyBase):
    __tablename__ = 'matches'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    team1_defender: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    team1_attacker: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    team2_defender: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    team2_attacker: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    goals_team1: int = sa.Column(sa.Integer, nullable=False)
    goals_team2: int = sa.Column(sa.Integer, nullable=False)
    created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
