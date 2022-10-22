from datetime import datetime
from typing import Optional
import random

from pydantic import BaseModel, validator
from app.config import settings


def get_profile_pic_url_from_nickname(nickname: str) -> str:
    random.seed(nickname)
    image_number = random.choices(list(range(1, 906)))[0]
    return f"{settings.BLOB_STORAGE_BASE_URL}/{settings.BLOB_PROFILE_IMAGE_CONTAINER}/pokemons/{image_number}.png"


class UserReadUnauthorized(BaseModel):
    id: int
    nickname: str
    motto: Optional[str]
    profile_pic_path: Optional[str] = None
    created_dt: datetime

    @validator('profile_pic_path')
    def set_profile_pic_path(cls, v, values):
        return v or get_profile_pic_url_from_nickname(values['nickname'])


class UserRead(UserReadUnauthorized):
    email: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    motto: Optional[str] = None
    profile_pic_path: Optional[str] = None
    password: Optional[str] = None
