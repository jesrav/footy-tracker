import datetime
import sqlalchemy as sa
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nickname: str = sa.Column(sa.String, unique=True, nullable=False)
    email: str = sa.Column(sa.String, index=True, unique=True, nullable=False)
    hash_password: str = sa.Column(sa.String, nullable=False)
    created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow, index=True)
    last_login: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow, index=True)


class Team(SqlAlchemyBase):
    __tablename__ = 'teams'
    __table_args__ = (UniqueConstraint('defender_user_id', 'attacker_user_id', name='_defender_attacker_uc'),)

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    defender_user_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    attacker_user_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow, index=True)

    defender = relationship("User", foreign_keys=[defender_user_id])
    attacker = relationship("User", foreign_keys=[attacker_user_id])


class Result(SqlAlchemyBase):
    __tablename__ = 'results'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    submitter_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    team1_id: int = sa.Column(sa.Integer, ForeignKey("teams.id"), nullable=False)
    team2_id: int = sa.Column(sa.Integer, ForeignKey("teams.id"), nullable=False)
    goals_team1: int = sa.Column(sa.Integer, nullable=False)
    goals_team2: int = sa.Column(sa.Integer, nullable=False)
    created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow, index=True)

    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team1_id])


class ResultApproval(SqlAlchemyBase):
    __tablename__ = 'result_approvals'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    result_submission_id: int = sa.Column(sa.Integer, ForeignKey("results.id"), nullable=False)
    reviewer_id: int =sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    approved: bool = sa.Column(sa.Boolean)
    created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow, index=True)


# class Rating(SqlAlchemyBase):
#     __tablename__ = 'ratings'
#
#     id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     user: int = sa.Column(sa.Integer)
#     last_match_used_for_calculation: int = sa.Column(sa.Integer)
#     created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)
