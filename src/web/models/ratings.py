from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserRating(BaseModel):
    id: int
    user_id: int
    rating: float
    latest_result_at_update_id: Optional[int]
    created_dt: datetime

