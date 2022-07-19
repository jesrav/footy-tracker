from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    nickname: str
    email: str
    created_date: datetime
    last_login: datetime
