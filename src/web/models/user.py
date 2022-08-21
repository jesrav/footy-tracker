from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    nickname: str
    email: str
    motto: Optional[str]
    profile_pic_path: str
    created_dt: datetime
