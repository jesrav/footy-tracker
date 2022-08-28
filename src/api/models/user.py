import os
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, AnyUrl, root_validator
from sqlmodel import SQLModel, Field, Relationship

from models.ranking import UserRanking, UserRankingRead


BLOB_STORAGE_BASE_URL = os.environ["BLOB_STORAGE_BASE_URL"]


class UserBase(SQLModel):
    nickname: str
    email: EmailStr
    motto: Optional[str] = None
    profile_pic_path: str = BLOB_STORAGE_BASE_URL + "defaultuser.png"


class User(UserBase, table=True):
    id: Optional[int] = Field(index=True, primary_key=True)
    hash_password: str
    created_dt: datetime = Field(default_factory=datetime.utcnow)
    ratings: List["UserRating"] = Relationship(back_populates="user")
    ranking: UserRanking = Relationship()

    @property
    def latest_rating(self):
        return sorted(self.ratings, key=lambda x: x.created_dt, reverse=True)[0]


class UserCreate(UserBase):
    password: str


class UserUpdate(SQLModel):
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    motto: Optional[str] = None
    profile_pic_path: Optional[str] = None
    password: Optional[str] = None

    @root_validator(pre=False)
    def must_have_at_least_one_update(cls, values):
        if not (
            values.get('nickname')
            or values.get('email')
            or values.get('motto')
            or values.get('profile_pic_path')
            or values.get('password')
        ):
            raise ValueError(
                'Update must have a non null value for one of the attributes: '
                'nickname, email, motto, profile_pic_path or password'
            )
        return values


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    created_dt: datetime

