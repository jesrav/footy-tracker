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
    def win_rate(self) -> str:
        if (self.games_played_defence + self.games_played_offence) == 0:
            return "NaN"
        win_rate = 100 * (
            (self.games_won_defence + self.games_won_offence)
            / (self.games_played_defence + self.games_played_offence)
        )
        return '{:.0f}'.format(win_rate) + '%'

    @property
    def win_rate_defence(self) -> str:
        if self.games_played_defence == 0:
            return "NaN"
        win_rate = 100 * (self.games_won_defence / self.games_played_defence)
        return '{:.0f}'.format(win_rate) + '%'

    @property
    def win_rate_offence(self) -> str:
        if self.games_played_offence == 0:
            return "NaN"
        win_rate = 100 * (self.games_won_offence / self.games_played_offence)
        return '{:.0f}'.format(win_rate) + '%'
