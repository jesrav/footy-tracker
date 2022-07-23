from datetime import datetime

from pydantic import BaseModel

from models.team import TeamBase


class ResultBase(BaseModel):
    submitter_id: int
    team1: TeamBase
    team2: TeamBase
    goals_team1: int
    goals_team2: int


class Result(BaseModel):
    id: int
    team1: TeamBase
    team2: TeamBase
    goals_team1: int
    goals_team2: int
    created_date: datetime
