from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserRatingCreate(BaseModel):
    user_id: int
    rating: float
    latest_result_at_update_id: Optional[int]


class UserRatingRead(UserRatingCreate):
    id: int
    created_dt: datetime

    def get_new_rating(self, rating_delta: float) -> UserRatingCreate:
        return UserRatingCreate(
            user_id=self.user_id,
            rating=self.rating + rating_delta
        )

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    nickname: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(UserBase):
    id: int
    created_dt: datetime
    latest_rating: UserRatingRead

    class Config:
        orm_mode = True


class TeamCreate(BaseModel):
    defender_user_id: int
    attacker_user_id: int

    class Config:
        orm_mode = True


class TeamRead(BaseModel):
    defender: UserRead
    attacker: UserRead
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


class ResultSubmissionRead(BaseModel):
    id: int
    submitter: UserRead
    team1: TeamRead
    team2: TeamRead
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator: Optional[UserRead]
    validation_dt: Optional[datetime]
    created_dt: datetime

    class Config:
        orm_mode = True

