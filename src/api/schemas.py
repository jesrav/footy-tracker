from datetime import datetime

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
    created_date: datetime
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
    created_date: datetime

    class Config:
        orm_mode = True


class ResultBase(BaseModel):
    submitter_id: int
    team1: TeamBase
    team2: TeamBase
    goals_team1: int
    goals_team2: int


class Result(ResultBase):
    id: int
    created_date: datetime

    class Config:
        orm_mode = True


class ResultApprovalBase(BaseModel):
    result_submission_id: int
    reviewer_id: int
    approved: bool


class ResultApproval(BaseModel):
    id: int
    created_date: datetime

    class Config:
        orm_mode = True
