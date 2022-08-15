from typing import Optional, List

from starlette.requests import Request

from models.ratings import UserRating
from models.result import ResultSubmissionRead
from models.user import UserRead
from services import user_service, tracking_service
from viewmodels.shared.viewmodel import ViewModelBase


class LeaderboardViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user: Optional[UserRead] = None
        self.latest_user_ratings: List[UserRating] = []

    async def load(self):
        self.user = await user_service.get_user_by_id(self.user_id)
        self.latest_user_ratings = await tracking_service.get_latest_user_ratings()
        self.latest_user_ratings = sorted(self.latest_user_ratings, key=lambda x: x.rating, reverse=True)

        for i, user_rating in enumerate(self.latest_user_ratings, start=1):
            user_rating.ranking = i
