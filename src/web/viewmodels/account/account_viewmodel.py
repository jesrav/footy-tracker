from typing import Optional, List

from starlette.requests import Request

from models.ratings import UserRating
from models.user import UserRead
from models.result import ResultSubmissionRead, ResultForUserValidation
from services import user_service, tracking_service
from viewmodels.shared.viewmodel import ViewModelBase


class AccountViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user: Optional[UserRead] = None
        self.latest_ratings: List[UserRating] = []
        self.user_ratings: List[UserRating] = []
        self.latest_results = List[ResultSubmissionRead]
        self.latest_user_rating: Optional[UserRating] = None
        self.results_to_approve: List[ResultSubmissionRead] = []
        self.results_for_opposition_to_approve: List[ResultSubmissionRead] = []


        self.result_id: Optional[int] = None
        self.approved: Optional[bool] = None

    async def load(self):
        self.user = await user_service.get_user_by_id(self.user_id)
        self.latest_results = await tracking_service.get_approved_results()
        user_ratings = await tracking_service.get_user_ratings(self.user_id)
        self.user_ratings = [(r.created_dt.strftime("%Y-%m-%d, %H:%M:%S"), r.rating) for r in sorted(user_ratings, key= lambda x: x.created_dt)]
        results_to_approve = await tracking_service.get_results_for_approval_by_user(self.user_id)
        results_for_opposition_to_approve = await tracking_service.get_results_for_approval_submitted_by_users_team(self.user_id)
        self.latest_user_rating = await tracking_service.get_latest_user_rating(self.user_id)

        self.results_to_approve = [
            ResultForUserValidation.from_result_submission(
                user_id=self.user_id,
                result=r,
            ) for r in results_to_approve
        ]
        self.results_for_opposition_to_approve = [
            ResultForUserValidation.from_result_submission(
                user_id=self.user_id,
                result=r,
            ) for r in results_for_opposition_to_approve
        ]

    async def load_form(self):
        form = await self.request.form()
        self.result_id = int(form.get('result_id'))
        if form.get('approved') == "false":
            self.approved = False
        if form.get('approved') == "true":
            self.approved = True
