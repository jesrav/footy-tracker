from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class UserRead(BaseModel):
    id: int
    nickname: str
    email: str
    motto: Optional[str]
    profile_pic_path: Optional[str] = None
    created_dt: datetime

    @validator('profile_pic_path')
    def set_profile_pic_path(cls, profile_pic_path):
        return profile_pic_path or "/static/img/defaultuser.png"


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    motto: Optional[str] = None
    profile_pic_path: Optional[str] = None
    password: Optional[str] = None
