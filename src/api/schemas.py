from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    nickname: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_date: datetime
    last_login: datetime

    class Config:
        orm_mode = True


class TeamCreate(BaseModel):
    defender_user_id: int
    attacker_user_id: int


class Team(TeamCreate):
    id: int
    created_date: datetime


class MatchCreate(BaseModel):
    team1: TeamCreate
    team2: TeamCreate
    goals_team1: int
    goals_team2: int


class Match(MatchCreate):
    id: int
    created_date: datetime

    class Config:
        orm_mode = True


# class MatchBase(BaseModel):
#     team1_defender_id: int= sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
#     team1_attacker_id: int
#     team2_defender_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
#     team2_attacker_id: int = sa.Column(sa.Integer, ForeignKey("users.id"), nullable=False)
#     goals_team1: int = sa.Column(sa.Integer, nullable=False)
#     goals_team2: int = sa.Column(sa.Integer, nullable=False)
#     created_date: datetime.datetime = sa.Column(sa.DateTime, default=datetime.datetime.now, index=True)