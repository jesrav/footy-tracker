from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from models.team import TeamRead, TeamCreate
from models.user import UserReadUnauthorized


class ResultSubmissionCreate(BaseModel):
    submitter_id: int
    team1: TeamCreate
    team2: TeamCreate
    goals_team1: int
    goals_team2: int


class ResultSubmissionRead(BaseModel):
    id: int
    submitter: UserReadUnauthorized
    team1: TeamRead
    team2: TeamRead
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator: Optional[UserReadUnauthorized]
    validation_dt: Optional[datetime]
    created_dt: datetime


class ResultForUserDisplay(BaseModel):
    id: int
    submitter: UserReadUnauthorized
    win: bool
    user_position: str
    teammate: UserReadUnauthorized
    opposing_defender: UserReadUnauthorized
    opposing_attacker: UserReadUnauthorized
    goals_user_team: int
    goals_opposing_team: int
    created_dt: datetime

    @classmethod
    def from_result_submission(
        cls, user_id: int, result: ResultSubmissionRead
    ) -> 'ResultForUserDisplay':
        if result.team1.user_in_team(user_id):
            return ResultForUserDisplay(
                id=result.id,
                submitter=result.submitter,
                win=result.goals_team1 > result.goals_team2,
                user_position=result.team1.get_user_position(user_id),
                teammate=result.team1.get_teammate(user_id),
                opposing_defender=result.team2.defender,
                opposing_attacker=result.team2.attacker,
                goals_user_team=result.goals_team1,
                goals_opposing_team=result.goals_team2,
                created_dt=result.created_dt
            )
        elif result.team2.user_in_team(user_id):
            return ResultForUserDisplay(
                id=result.id,
                submitter=result.submitter,
                win=result.goals_team2 > result.goals_team1,
                user_position=result.team2.get_user_position(user_id),
                teammate = result.team2.get_teammate(user_id),
                opposing_defender = result.team1.defender,
                opposing_attacker = result.team1.attacker,
                goals_user_team = result.goals_team2,
                goals_opposing_team = result.goals_team1,
                created_dt=result.created_dt
            )
        else:
            raise ValueError("User must on one of the teams.")
