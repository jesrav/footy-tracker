from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.user import UserReadUnauthorized


class UserRating(BaseModel):
    id: int
    user: UserReadUnauthorized
    rating_defence: float
    rating_offence: float
    overall_rating: float
    latest_result_at_update_id: Optional[int]
    created_dt: datetime

