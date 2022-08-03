from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from models.user import User, UserRead


class Team(SQLModel, table=True):
    id: Optional[int] = Field(index=True, primary_key=True)
    defender_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    attacker_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_dt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    defender: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Team.defender_user_id]"))
    attacker: User = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Team.attacker_user_id]"))

    def user_in_team(self, user_id: int) -> bool:
        return user_id in [self.defender.id, self.attacker.id]

    def get_team_members(self) -> List[User]:
        return [self.defender, self.attacker]

    def get_teammate(self, user_id) -> Optional[User]:
        if not self.user_in_team(user_id):
            return None
        else:
            return [user for user in self.get_team_members() if user.id != user_id][0]


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
