import ast
from typing import List, Optional

from starlette.requests import Request

from models.result import ResultSubmissionCreate
from models.team import TeamCreate
from models.user import UserReadUnauthorized
from models.validation_error import ValidationError
from services import user_service, tracking_service
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
        self.users: Optional[List[UserReadUnauthorized]] = None
        self.error: Optional[str] = None

    async def load(self):
        self.users = await user_service.get_all_users()

    async def post_form(self):
        form = await self.request.form()
        self.team1_defender = form.get('team1_defender')
        self.team1_attacker = form.get('team1_attacker')
        self.team2_defender = form.get('team2_defender')
        self.team2_attacker = form.get('team2_attacker')
        self.goals_team1 = form.get('goals_team1')
        self.goals_team2 = form.get('goals_team2')
        self.users = await user_service.get_all_users()

        if not all([
            self.team1_defender != "",
            self.team1_attacker != "",
            self.team2_defender != "",
            self.team2_attacker != "",
            self.goals_team1 != "",
            self.goals_team2 != "",
            ]):
            self.error = "All fields need to be filled."

        elif len({
                self.team1_defender,
                self.team1_attacker,
                self.team2_defender,
                self.team2_attacker,
            }) != 4:
                self.error = "Match contestants must be 4 unique users."

        elif self.goals_team1 == self.goals_team2:
            self.error = "A table soccer match must have a winner. Please finish the match!"

        elif self.user_id not in [
            int(self.team1_defender),
            int(self.team1_attacker),
            int(self.team2_defender),
            int(self.team2_attacker)
        ]:
            self.error = "Submitter must be part of the match!"

        else:
            # Try to Create result registration
            try:
                result = ResultSubmissionCreate(
                    submitter_id=self.user_id,
                    team1=TeamCreate(
                        defender_user_id=self.team1_defender,
                        attacker_user_id=self.team1_attacker,
                    ),
                    team2=TeamCreate(
                        defender_user_id=self.team2_defender,
                        attacker_user_id=self.team2_attacker,
                    ),
                    goals_team1=self.goals_team1,
                    goals_team2=self.goals_team2,
                )
                _ = await tracking_service.register_result(result, bearer_token=self.bearer_token)
            except ValidationError as e:
                self.error = e.error_msg
