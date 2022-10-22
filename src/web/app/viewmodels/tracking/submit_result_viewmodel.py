from typing import List, Optional

from starlette.requests import Request

from app.models.result import ResultSubmissionCreate
from app.models.team import TeamCreate
from app.models.user import UserReadUnauthorized
from app.models.validation_error import ValidationError
from app.services import user_service, tracking_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class SubmitResultViewModel(ViewModelBase):
    def __init__(
        self,
        request: Request,
        team1_defender_id: Optional[int] = None,
        team1_attacker_id: Optional[int] = None,
        team2_defender_id: Optional[int] = None,
        team2_attacker_id: Optional[int] = None,
    ):
        super().__init__(request)
        self.team1_defender_id = team1_defender_id
        self.team1_attacker_id = team1_attacker_id
        self.team2_defender_id = team2_defender_id
        self.team2_attacker_id = team2_attacker_id
        self.team1_defender: Optional[UserReadUnauthorized] = None
        self.team1_attacker: Optional[UserReadUnauthorized] = None
        self.team2_defender: Optional[UserReadUnauthorized] = None
        self.team2_attacker: Optional[UserReadUnauthorized] = None
        self.goals_team1: Optional[int] = None
        self.goals_team2: Optional[int] = None
        self.users: Optional[List[UserReadUnauthorized]] = None
        self.error: Optional[str] = None

    async def load(self):
        self.users = await user_service.get_all_users()
        if self.team1_defender_id is not None:
            self.team1_defender = [u for u in self.users if u.id == self.team1_defender_id][0]
        if self.team1_attacker_id is not None:
            self.team1_attacker = [u for u in self.users if u.id == self.team1_attacker_id][0]
        if self.team2_defender_id is not None:
            self.team2_defender = [u for u in self.users if u.id == self.team2_defender_id][0]
        if self.team2_attacker_id is not None:
            self.team2_attacker = [u for u in self.users if u.id == self.team2_attacker_id][0]

    async def post_form(self):
        form = await self.request.form()
        self.team1_defender_id = form.get('team1_defender')
        self.team1_attacker_id = form.get('team1_attacker')
        self.team2_defender_id = form.get('team2_defender')
        self.team2_attacker_id = form.get('team2_attacker')
        self.team1_defender_id = int(self.team1_defender_id) if self.team1_defender_id else None
        self.team1_attacker_id = int(self.team1_attacker_id) if self.team1_attacker_id else None
        self.team2_defender_id = int(self.team2_defender_id) if self.team2_defender_id else None
        self.team2_attacker_id = int(self.team2_attacker_id) if self.team2_attacker_id else None
        self.goals_team1 = form.get('goals_team1')
        self.goals_team2 = form.get('goals_team2')
        await self.load()

        if not all([
            self.team1_defender_id is not None,
            self.team1_attacker_id is not None,
            self.team2_defender_id is not None,
            self.team2_attacker_id is not None,
            self.goals_team1 != "",
            self.goals_team2 != "",
            ]):
            self.error = "All fields need to be filled."

        elif len({
                self.team1_defender_id,
                self.team1_attacker_id,
                self.team2_defender_id,
                self.team2_attacker_id,
            }) != 4:
                self.error = "Match contestants must be 4 unique users."

        elif self.goals_team1 == self.goals_team2:
            self.error = "A table soccer match must have a winner. Please finish the match!"

        elif self.user_id not in [
            int(self.team1_defender_id),
            int(self.team1_attacker_id),
            int(self.team2_defender_id),
            int(self.team2_attacker_id)
        ]:
            self.error = "Submitter must be part of the match!"

        else:
            # Try to Create result registration
            try:
                result = ResultSubmissionCreate(
                    submitter_id=self.user_id,
                    team1=TeamCreate(
                        defender_user_id=self.team1_defender_id,
                        attacker_user_id=self.team1_attacker_id,
                    ),
                    team2=TeamCreate(
                        defender_user_id=self.team2_defender_id,
                        attacker_user_id=self.team2_attacker_id,
                    ),
                    goals_team1=self.goals_team1,
                    goals_team2=self.goals_team2,
                )
                _ = await tracking_service.register_result(result, bearer_token=self.bearer_token)
            except ValidationError as e:
                self.error = e.error_msg
