from datetime import datetime

from pydantic import BaseModel


class UserStats(BaseModel):
    id: int
    user_id: int
    eggs_received: int
    eggs_given: int
    games_played_defence: int
    games_played_offence: int
    games_won_defence: int
    games_won_offence: int
    created_dt: datetime
