import ast
from typing import List, Optional

from starlette.requests import Request

from models.team import UsersForTeamsSuggestion, TeamsSuggestion
from models.user import UserReadUnauthorized
from models.validation_error import ValidationError
from services import ml_service, user_service
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
            # Try to get a team suggestion
            try:
                self.suggested_teams = await ml_service.get_teams_suggestion(
                    users=UsersForTeamsSuggestion(
                        user_id_1=self.user1,
                        user_id_2=self.user2,
                        user_id_3=self.user3,
                        user_id_4=self.user4,
                    ),
                    bearer_token=self.bearer_token
                )
            except ValidationError as e:
                self.error = e.error_msg
