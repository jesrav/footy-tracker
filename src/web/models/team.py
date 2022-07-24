from datetime import datetime

from pydantic import BaseModel


class TeamBase(BaseModel):
    defender_user_id: int
    attacker_user_id: int


class Team(TeamBase):
    id: int
    created_dt: datetime
