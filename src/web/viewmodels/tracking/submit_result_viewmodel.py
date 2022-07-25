from typing import List, Optional

from starlette.requests import Request

from models.user import UserOut
from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


class SubmitResultViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)

        self.team1_defender: Optional[int] = None
        self.team1_attacker: Optional[int] = None
        self.team2_defender: Optional[int] = None
        self.team2_attacker: Optional[int] = None
        self.goals_team1: Optional[int] = None
        self.goals_team2: Optional[int] = None
        self.users: Optional[List[UserOut]] = None

    async def load(self):
        self.users: List[UserOut] = await user_service.get_all_users()

    async def load_form(self):
        form = await self.request.form()
        self.team1_defender = int(form.get('team1_defender'))
        self.team1_attacker = int(form.get('team1_attacker'))
        self.team2_defender = int(form.get('team2_defender'))
        self.team2_attacker = int(form.get('team2_attacker'))
        self.goals_team1 = int(form.get('goals_team1'))
        self.goals_team2 = int(form.get('goals_team2'))

        if not all([
            self.team1_defender,
            self.team1_attacker,
            self.team2_defender,
            self.team2_attacker,
            self.goals_team1,
            self.goals_team2,
            ]):
            self.error = "All fields need to be filled."
