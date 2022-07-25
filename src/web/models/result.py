from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.team import Team, TeamBase
from models.user import User


class ResultSubmissionBase(BaseModel):
    submitter_id: int
    team1: TeamBase
    team2: TeamBase
    goals_team1: int
    goals_team2: int


class ResultSubmission(BaseModel):
    submitter: User
    team1: Team
    team2: Team
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator: Optional[User]

