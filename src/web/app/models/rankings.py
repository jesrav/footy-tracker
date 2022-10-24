from datetime import datetime

from pydantic import BaseModel


class UserRanking(BaseModel):
    id: int
    user_id: int
    defensive_ranking: int
    offensive_ranking: int
    overall_ranking: int
    updated_dt: datetime

