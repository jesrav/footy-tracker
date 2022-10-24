from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class UserRanking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    defensive_ranking: int
    offensive_ranking: int
    overall_ranking: int
    updated_dt: datetime = Field(default_factory=datetime.utcnow)


class UserRankingRead(SQLModel):
    id: int
    user_id: int
    defensive_ranking: int
    offensive_ranking: int
    overall_ranking: int
    updated_dt: datetime
