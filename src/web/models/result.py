from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from models.team import TeamOut, TeamCreate
from models.user import UserOut


class ResultSubmissionCreate(BaseModel):
    submitter_id: int
    team1: TeamCreate
    team2: TeamCreate
    goals_team1: int
    goals_team2: int


class ResultSubmissionOut(BaseModel):
    id: int
    submitter: UserOut
    team1: TeamOut
    team2: TeamOut
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator: Optional[UserOut]
    validation_dt: Optional[datetime]
    created_dt: datetime

