from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.user import UserRead


class UserRating(BaseModel):
    id: int
    ranking: Optional[int]
    user: UserRead
    rating_defence: float
    rating_offence: float
    latest_result_at_update_id: Optional[int]
    created_dt: datetime

    @property
    def rating(self):
        return (self.rating_defence + self.rating_offence) / 2

