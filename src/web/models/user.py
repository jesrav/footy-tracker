from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    nickname: str
    email: str
    created_dt: datetime
    last_login: datetime
