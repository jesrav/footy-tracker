from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from models.user import UserRead


class TeamCreate(BaseModel):
    defender_user_id: int
    attacker_user_id: int


class TeamRead(BaseModel):
    defender: UserRead
    attacker: UserRead
    id: int
    created_dt: datetime

    def user_in_team(self, user_id: int) -> bool:
        return user_id in [self.defender.id, self.attacker.id]

    def get_team_members(self) -> List[UserRead]:
        return [self.defender, self.attacker]

    def get_user_position(self, user_id: int) -> bool:
        if user_id == self.defender.id:
            return 'defender'
        elif user_id == self.attacker.id:
            return 'attacker'
        else:
            return None

    def get_teammate(self, user_id) -> Optional[UserRead]:
        if not self.user_in_team(user_id):
            return None
        else:
            return [user for user in self.get_team_members() if user.id != user_id][0]