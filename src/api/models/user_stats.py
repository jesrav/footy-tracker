from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class UserStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    eggs_received: int = Field(default=0)
    eggs_given: int = Field(default=0)
    games_played_defence: int = Field(default=0)
    games_played_offence: int = Field(default=0)
    games_won_defence: int = Field(default=0)
    games_won_offence: int = Field(default=0)
    created_dt: datetime = Field(default_factory=datetime.utcnow)
