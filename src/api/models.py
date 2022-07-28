import datetime
import sqlalchemy as sa
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from database import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nickname: str = sa.Column(sa.String, unique=True, nullable=False)
    email: str = sa.Column(sa.String, index=True, unique=True, nullable=False)
    hash_password: str = sa.Column(sa.String, nullable=False)
    created_dt: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow, index=True)

    ratings = relationship("UserRating")

    @hybrid_property
    def latest_rating(self):
        return sorted(self.ratings, key=lambda x: x.created_dt, reverse=True)[0]


class Team(SqlAlchemyBase):
    __tablename__ = 'teams'
    __table_args__ = (UniqueConstraint('defender_user_id', 'attacker_user_id', name='_defender_attacker_uc'),)

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    defender_user_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    attacker_user_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    created_dt: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow, index=True)

    defender = relationship("User", foreign_keys=[defender_user_id])
    attacker = relationship("User", foreign_keys=[attacker_user_id])


class ResultSubmission(SqlAlchemyBase):
    __tablename__ = 'result_submissions'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    submitter_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    team1_id: int = sa.Column(sa.Integer, ForeignKey("teams.id"), nullable=False)
    team2_id: int = sa.Column(sa.Integer, ForeignKey("teams.id"), nullable=False)
    goals_team1: int = sa.Column(sa.Integer, nullable=False)
    goals_team2: int = sa.Column(sa.Integer, nullable=False)
    created_dt: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow, index=True)
    approved: bool = sa.Column(sa.Boolean)
    validator_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=True)
    validation_dt: datetime.datetime = sa.Column(sa.DateTime)

    submitter = relationship("User", foreign_keys=[submitter_id])
    validator = relationship("User", foreign_keys=[validator_id])
    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])


class UserRating(SqlAlchemyBase):
    __tablename__ = 'user_ratings'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
    rating: float = sa.Column(sa.Float, nullable=False)
    latest_result_at_update_id: int = sa.Column(sa.Integer, ForeignKey("result_submissions.id"), nullable=True)
    created_dt: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="ratings")