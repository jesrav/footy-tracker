from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator as pydantic_validator


class UserBase(BaseModel):
    nickname: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(UserBase):
    id: int
    created_dt: datetime
    last_login: datetime

    class Config:
        orm_mode = True


class TeamCreate(BaseModel):
    defender_user_id: int
    attacker_user_id: int

    class Config:
        orm_mode = True


class TeamOut(BaseModel):
    defender: UserOut
    attacker: UserOut
    id: int
    created_dt: datetime


    class Config:
        orm_mode = True


class ResultSubmissionCreate(BaseModel):
    submitter_id: int
    team1: TeamCreate
    team2: TeamCreate
    goals_team1: int
    goals_team2: int


class ResultSubmissionOut(BaseModel):
    id: int
    submitter: UserOut
    team1: TeamOut
    team2: TeamOut
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator: Optional[UserOut]
    validation_dt: Optional[datetime]
    created_dt: datetime

    class Config:
        orm_mode = True
