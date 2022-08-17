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

    @property
    def win_rate(self):
        if (self.games_played_defence + self.games_played_offence) == 0:
            return "NaN"
        return 100 * (
            (self.games_won_defence + self.games_won_offence)
            / (self.games_played_defence + self.games_played_offence)
        )

    @property
    def win_rate_defence(self):
        if self.games_played_defence == 0:
            return "NaN"
        return 100 * (self.games_won_defence / self.games_played_defence)

    @property
    def win_rate_offence(self):
        if self.games_played_offence == 0:
            return "NaN"
        return 100 * (self.games_won_offence / self.games_played_offence)
