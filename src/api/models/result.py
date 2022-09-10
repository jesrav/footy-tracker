from datetime import datetime
from typing import Optional

from pydantic import root_validator
from sqlmodel import SQLModel, Field, Relationship

from models.team import Team, TeamCreate, TeamRead
from models.user import User, UserReadUnauthorized


class ResultSubmission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    submitter_id: int = Field(default=None, foreign_key="user.id")
    team1_id: int = Field(default=None, foreign_key="team.id")
    team2_id: int = Field(default=None, foreign_key="team.id")
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    validation_dt: Optional[datetime]
    created_dt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    submitter: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.submitter_id]"))
    validator: Optional[User] = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.validator_id]"))
    team1: Team = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.team1_id]"))
    team2: Team = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.team2_id]"))

    @property
    def match_participants(self):
        return [
            self.team1.defender_user_id,
            self.team1.attacker_user_id,
            self.team2.defender_user_id,
            self.team2.attacker_user_id
        ]


class ResultSubmissionCreate(SQLModel):
    team1: TeamCreate
    team2: TeamCreate
    goals_team1: int
    goals_team2: int

    @root_validator(pre=False)
    def result_must_have_winner(cls, values):
        if values.get('goals_team1') == values.get('goals_team2'):
            raise ValueError('Result must have winner. goals_team1 must be different than goals_team2')
        return values

    @root_validator(pre=False)
    def all_contestants_must_differ(cls, values):
        team1 = values.get('team1')
        team2 = values.get('team2')
        if team1 and team2 and len(
            {team1.defender_user_id, team1.attacker_user_id, team2.defender_user_id, team2.attacker_user_id}
        ) != 4:
            raise ValueError('Match contestants must be 4 unique users.')
        return values


class ResultSubmissionRead(SQLModel):
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
