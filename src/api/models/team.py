from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from models.user import User, UserRead


class Team(SQLModel, table=True):
    id: Optional[int] = Field(index=True, primary_key=True)
    defender_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    attacker_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_dt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    defender: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Team.defender_user_id]"))
    attacker: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Team.attacker_user_id]"))


class TeamBase(SQLModel):
    defender_user_id: int
    attacker_user_id: int


class TeamCreate(TeamBase):
    pass


class TeamRead(SQLModel):
    id: int
    defender: UserRead
    attacker: UserRead
    created_dt: datetime