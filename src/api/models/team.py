from datetime import datetime
from typing import Optional, List

from pydantic import validator, root_validator
from sqlmodel import SQLModel, Field, Relationship

from models.user import User, UserRead


class Team(SQLModel, table=True):
    id: Optional[int] = Field(index=True, primary_key=True)
    defender_user_id: int = Field(default=None, foreign_key="user.id")
    attacker_user_id: int = Field(default=None, foreign_key="user.id")
    created_dt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    defender: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Team.defender_user_id]"))
    attacker: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Team.attacker_user_id]"))


class TeamCreate(SQLModel):
    defender_user_id: int
    attacker_user_id: int

    @root_validator()
    def teammates_not_the_same(cls, values):
        defender_user_id, attacker_user_id = values.get('defender_user_id'), values.get('attacker_user_id')
        if defender_user_id == attacker_user_id:
            raise ValueError('Defender and attacker can not have the same user id.')
        return values

    def user_in_team(self, user_id: int) -> bool:
        return user_id in [self.defender_user_id, self.attacker_user_id]


class TeamRead(SQLModel):
    id: int
    defender: UserRead
    attacker: UserRead
    created_dt: datetime