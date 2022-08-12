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

    async def load(self):
        self.user = await user_service.get_user_by_id(self.user_id)

