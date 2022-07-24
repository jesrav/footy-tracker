from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    nickname: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class User(UserBase):
    id: int
    created_dt: datetime
    last_login: datetime

    class Config:
        orm_mode = True


class TeamBase(BaseModel):
    defender_user_id: int
    attacker_user_id: int

    class Config:
        orm_mode = True


class Team(TeamBase):
    id: int
    created_dt: datetime

    class Config:
        orm_mode = True


class ResultSubmissionBase(BaseModel):
    submitter_id: int
    team1: TeamBase
    team2: TeamBase
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator_id: Optional[int]


class ResultSubmission(ResultSubmissionBase):
    id: int
    created_dt: datetime
    validation_dt: Optional[datetime]

    class Config:
        orm_mode = True

#
# class ResultApprovalBase(BaseModel):
#     result_submission_id: int
#     reviewer_id: int
#     approved: Optional[bool]
#
#
# class ResultApproval(BaseModel):
#     id: int
#     created_dt: datetime
#
#     class Config:
#         orm_mode = True
