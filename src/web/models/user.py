import os
from datetime import datetime
from typing import Optional
import random

from pydantic import BaseModel, validator


BLOB_STORAGE_BASE_URL = os.environ['BLOB_STORAGE_BASE_URL']

def get_profile_pic_url_from_email(email: str) -> str:
    random.seed(email)
    image_number = random.choices(list(range(1, 906)))[0]
    return f"{BLOB_STORAGE_BASE_URL}pokemons/{image_number}.png"


class UserRead(BaseModel):
    id: int
    nickname: str
    email: str
    motto: Optional[str]
    profile_pic_path: Optional[str] = None
    created_dt: datetime

    # @validator('profile_pic_path')
    # def set_profile_pic_path(cls, profile_pic_path):
    #     return profile_pic_path or get_profile_pic_url_from_email(self.email)

    @validator('profile_pic_path')
    def set_profile_pic_path(cls, v, values):
        if "profile_pic_path" in values:
            return values['profile_pic_path']
        else:
            return get_profile_pic_url_from_email(values['email'])


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    motto: Optional[str] = None
    profile_pic_path: Optional[str] = None
    password: Optional[str] = None
