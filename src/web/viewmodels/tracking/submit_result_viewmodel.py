from typing import List, Optional

from starlette.requests import Request

from src.web.data.user import User
from src.web.services import user_service
from src.web.viewmodels.shared.viewmodel import ViewModelBase


class SubmitResultViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)

        self.users: List[User] = user_service.get_all_users()
        self.team1_defender: Optional[int] = None
        self.team1_attacker: Optional[int] = None
        self.team2_defender: Optional[int] = None
        self.team2_attacker: Optional[int] = None
        self.goals_team1: Optional[int] = None
        self.goals_team2: Optional[int] = None

    async def load(self):
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
