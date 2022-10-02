import ast
from typing import List, Optional

from starlette.requests import Request

from models.result import ResultSubmissionCreate
from models.team import TeamCreate, UsersForTeamsSuggestion, TeamsSuggestion
from models.user import UserReadUnauthorized
from models.validation_error import ValidationError
from services import user_service, tracking_service
from viewmodels.shared.viewmodel import ViewModelBase


class SuggestTeamsViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.users: Optional[List[UserReadUnauthorized]] = None
        self.user1: Optional[UserReadUnauthorized] = None
        self.user2: Optional[UserReadUnauthorized] = None
        self.user3: Optional[UserReadUnauthorized] = None
        self.user4: Optional[UserReadUnauthorized] = None
        self.suggested_teams: Optional[TeamsSuggestion] = None

    async def load(self):
        self.users = await user_service.get_all_users()

    async def post_form(self):
        form = await self.request.form()
        self.user1 = form.get('user1')
        self.user2 = form.get('user2')
        self.user3 = form.get('user3')
        self.user4 = form.get('user4')

        if not all([
            self.user1 != "",
            self.user2 != "",
            self.user3 != "",
            self.user4 != "",
            ]):
            self.error = "All fields need to be filled."

        elif len({
                self.user1,
                self.user2,
                self.user3,
                self.user4,
            }) != 4:
                self.error = "Match contestants must be 4 unique users."

        else:
            self.suggested_teams = TeamsSuggestion(
                team1=TeamCreate(defender_user_id=self.user1, attacker_user_id=self.user2),
                team2=TeamCreate(defender_user_id=self.user3, attacker_user_id=self.user4),
            )
            # # Try to get a team suggestion
            # try:
            #     result = ResultSubmissionCreate(
            #         submitter_id=self.user_id,
            #         team1=TeamCreate(
            #             defender_user_id=self.team1_defender,
            #             attacker_user_id=self.team1_attacker,
            #         ),
            #         team2=TeamCreate(
            #             defender_user_id=self.team2_defender,
            #             attacker_user_id=self.team2_attacker,
            #         ),
            #         goals_team1=self.goals_team1,
            #         goals_team2=self.goals_team2,
            #     )
            #     _ = await tracking_service.register_result(result, bearer_token=self.bearer_token)
            # except ValidationError as e:
            #     self.error = e.error_msg
