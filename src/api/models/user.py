from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

from models.rating import UserRating


class UserBase(SQLModel):
    nickname: str
    email: str


class User(UserBase, table=True):
    id: Optional[int] = Field(index=True, primary_key=True)
    hash_password: str
    created_dt: datetime = Field(default_factory=datetime.utcnow)

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