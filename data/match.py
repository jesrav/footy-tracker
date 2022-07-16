import datetime
import sqlalchemy as sa

from data.modelbase import SqlAlchemyBase


class Match(SqlAlchemyBase):
    __tablename__ = 'matches'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    team1_defender: int = sa.Column(sa.Integer)
    team1_atacker: int =  sa.Column(sa.Integer)
    team2_defender: int =  sa.Column(sa.Integer)
    team2_atacker: int =  sa.Column(sa.Integer)
    goals_team1: int =  sa.Column(sa.Integer)
    goals_team2: int =  sa.Column(sa.Integer)
    created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
