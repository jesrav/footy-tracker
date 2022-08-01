from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from models.team import Team, TeamCreate, TeamRead
from models.user import User, UserRead


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
    validator: Optional[
        User] = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.validator_id]"))
    team1: Team = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.team1_id]"))
    team2: Team = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ResultSubmission.team2_id]"))


class ResultSubmissionBase(SQLModel):
    submitter_id: int
    team1: TeamCreate
    team2: TeamCreate
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator_id: Optional[int]
    validation_dt: Optional[datetime]


class ResultSubmissionCreate(ResultSubmissionBase):
    pass


class ResultSubmissionRead(SQLModel):
    id: int
    submitter: UserRead
    team1: TeamRead
    team2: TeamRead
    goals_team1: int
    goals_team2: int
    approved: Optional[bool]
    validator: Optional[UserRead]
    validation_dt: Optional[datetime]
    created_dt: datetime