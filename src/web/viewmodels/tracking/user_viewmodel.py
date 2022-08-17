from typing import Optional, List

from starlette.requests import Request

from models.rankings import UserRanking
from models.ratings import UserRating
from models.user import UserRead
from models.result import ResultSubmissionRead, ResultForUserDisplay
from services import user_service, tracking_service
from viewmodels.shared.viewmodel import ViewModelBase


class UserViewModel(ViewModelBase):
    def __init__(self, user_in_view_id, request: Request):
        super().__init__(request)
        self.user: Optional[UserRead] = None
        self.user_in_view_id: int = user_in_view_id
        self.historical_user_ratings: List[UserRating] = []
        self.latest_results = List[ResultSubmissionRead]
        self.latest_user_rating: Optional[UserRating] = None
        self.user_ranking: Optional[UserRanking] = None

    async def load(self):
        self.user = await user_service.get_user_by_id(user_id=self.user_in_view_id)

        _latest_results_api_format = await tracking_service.get_approved_results(user_id=self.user_in_view_id)
        self.latest_results = [
            ResultForUserDisplay.from_result_submission(
                user_id=int(self.user_in_view_id),
                result=r,
            ) for r in _latest_results_api_format
        ]

        _historical_user_ratings = await tracking_service.get_user_ratings(user_id=self.user_in_view_id)
        self.historical_user_ratings = sorted(_historical_user_ratings, key= lambda x: x.created_dt)
        self.latest_user_rating = await tracking_service.get_latest_user_rating(user_id=self.user_in_view_id)
        user_rankings = await tracking_service.get_user_rankings()
        self.user_ranking = [user_ranking for user_ranking in user_rankings if user_ranking.user_id == self.user_id][0]
