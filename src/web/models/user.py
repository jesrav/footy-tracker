from datetime import datetime

from pydantic import BaseModel

from models.ratings import UserRating


class UserOut(BaseModel):
    id: int
    nickname: str
    email: str
    created_dt: datetime
    latest_rating: UserRating
