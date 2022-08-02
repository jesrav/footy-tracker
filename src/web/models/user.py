from datetime import datetime

from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    nickname: str
    email: str
    created_dt: datetime
