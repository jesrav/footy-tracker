from datetime import datetime

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
