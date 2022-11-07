from typing import List

from starlette.requests import Request

from app.models.result import ResultForUserDisplay
from app.services import tracking_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class IndexViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.results_to_approve: List[ResultForUserDisplay] = []
        self.results_for_opposition_to_approve: List[ResultForUserDisplay] = []

    async def load(self):
        results_to_approve = await tracking_service.get_results_for_approval_by_user(self.bearer_token)
        results_for_opposition_to_approve = await tracking_service.get_results_for_approval_submitted_by_users_team(self.bearer_token)
        self.results_to_approve = [
            ResultForUserDisplay.from_result_submission(
                user_id=self.user_id,
                result=r,
            ) for r in results_to_approve
        ]
        self.results_for_opposition_to_approve = [
            ResultForUserDisplay.from_result_submission(
                user_id=self.user_id,
                result=r,
            ) for r in results_for_opposition_to_approve
        ]
