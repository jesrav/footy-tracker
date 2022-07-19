from datetime import datetime

from pydantic import BaseModel

from models.team import TeamBase


class MatchBase(BaseModel):
    team1: TeamBase
    team2: TeamBase
    goals_team1: int
    goals_team2: int


class Match(BaseModel):
    id: int
    team1: TeamBase
    team2: TeamBase
    goals_team1: int
    goals_team2: int
    created_date: datetime
