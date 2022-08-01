from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class UserRating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    rating: float
    latest_result_at_update_id: Optional[int] = Field(default=None, foreign_key="resultsubmission.id")
    created_dt: Optional[datetime] = Field(default=datetime.utcnow())

    user: "User" = Relationship(back_populates="ratings")

    def get_new_rating(self, rating_delta: float) -> "UserRatingBase":
        return UserRatingCreate(
            user_id=self.user_id,
            rating=self.rating + rating_delta
        )


class UserRatingBase(SQLModel):
    user_id: int
    rating: float
    latest_result_at_update_id: Optional[int]


class UserRatingCreate(UserRatingBase):
    pass


class UserRatingRead(UserRatingBase):
    id: int
    created_dt: datetime


class UserBase(SQLModel):
    nickname: str
    email: str


class User(UserBase, table=True):
    id: Optional[int] = Field(index=True, primary_key=True)
    hash_password: str
    created_dt: datetime = Field(default=datetime.utcnow())

    ratings: List["UserRating"] = Relationship(back_populates="user")

    @property
    def latest_rating(self):
        return sorted(self.ratings, key=lambda x: x.created_dt, reverse=True)[0]


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(UserBase):
    id: int
    created_dt: datetime


class Team(SQLModel, table=True):
    id: Optional[int] = Field(index=True, primary_key=True)
    defender_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    attacker_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_dt: Optional[datetime] = Field(default=datetime.utcnow())

    defender: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Team.defender_user_id]"))
    attacker: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Team.attacker_user_id]"))


class TeamBase(SQLModel):
    defender_user_id: int
    attacker_user_id: int


class TeamCreate(TeamBase):
    pass


class TeamRead(SQLModel):
    id: int
    defender: UserRead
    attacker: UserRead
    created_dt: datetime


class ResultSubmission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    submitter_id: int = Field(default=None, foreign_key="user.id")
    team1_id: int = Field(default=None, foreign_key="team.id")
    team2_id: int = Field(default=None, foreign_key="team.id")
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    validation_dt: Optional[datetime]
    created_dt: Optional[datetime] = Field(default=datetime.utcnow())

    submitter: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.submitter_id]"))
    validator: Optional[User] = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.validator_id]"))
    team1: Team = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.team1_id]"))
    team2: Team = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.team2_id]"))


class ResultSubmissionBase(SQLModel):
    submitter_id: int
    team1: TeamCreate
    team2: TeamCreate
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator_id: Optional[int]
    validation_dt: Optional[datetime]


class ResultSubmissionCreate(ResultSubmissionBase):
    pass


class ResultSubmissionRead(SQLModel):
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

