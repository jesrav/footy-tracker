from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.team import TeamBase


class ResultSubmissionBase(BaseModel):
    submitter_id: int
    team1: TeamBase
    team2: TeamBase
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator_id: Optional[int]


class ResultSubmission(ResultSubmissionBase):
    id: int
    created_dt: datetime
    validation_dt: Optional[datetime]

