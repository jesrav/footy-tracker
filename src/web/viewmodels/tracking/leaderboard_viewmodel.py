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
