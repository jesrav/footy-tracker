from datetime import datetime

from pydantic import BaseModel

from models.user import User


class TeamBase(BaseModel):
    defender_user_id: int
    attacker_user_id: int


class Team(BaseModel):
    defender: User
    attacker: User
    id: int
    created_dt: datetime
