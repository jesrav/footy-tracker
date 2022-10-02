from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, root_validator

from models.user import UserReadUnauthorized


class TeamCreate(BaseModel):
    defender_user_id: int
    attacker_user_id: int


class TeamRead(BaseModel):
    defender: UserReadUnauthorized
    attacker: UserReadUnauthorized
    id: int
    created_dt: datetime

    def user_in_team(self, user_id: int) -> bool:
        return user_id in [self.defender.id, self.attacker.id]

    def get_team_members(self) -> List[UserReadUnauthorized]:
        return [self.defender, self.attacker]

    def get_user_position(self, user_id: int) -> Union[str, None]:
        if user_id == self.defender.id:
            return 'defender'
        elif user_id == self.attacker.id:
            return 'attacker'
        else:
            return None

    def get_teammate(self, user_id) -> Optional[UserReadUnauthorized]:
        if not self.user_in_team(user_id):
            return None
        else:
            return [user for user in self.get_team_members() if user.id != user_id][0]


class TeamsSuggestion(BaseModel):
    team1: TeamCreate
    team2: TeamCreate


class UsersForTeamsSuggestion(BaseModel):
    user_id_1: int
    user_id_2: int
    user_id_3: int
    user_id_4: int

    @root_validator()
    def users_unique(cls, values):
        users =[
            values.get('user_id_1'),
            values.get('user_id_2'),
            values.get('user_id_3'),
            values.get('user_id_4'),
        ]
        if len(set(users)) != len(users):
            raise ValueError("User id's must be unique.")
        return values
