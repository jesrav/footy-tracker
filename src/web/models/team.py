from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from models.user import UserOut


class TeamCreate(BaseModel):
    defender_user_id: int
    attacker_user_id: int


class TeamOut(BaseModel):
    defender: UserOut
    attacker: UserOut
    id: int
    created_dt: datetime

    def user_in_team(self, user_id: int) -> bool:
        return user_id in [self.defender.id, self.attacker.id]

    def get_team_members(self) -> List[UserOut]:
        return [self.defender, self.attacker]

    def get_teammate(self, user_id) -> Optional[UserOut]:
        if not self.user_in_team(user_id):
            return None
        else:
            return [user for user in self.get_team_members() if user.id != user_id][0]