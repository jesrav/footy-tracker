from typing import Optional, List

from starlette.requests import Request

from models.user import UserRead
from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


class AccountViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user: Optional[UserRead] = None

    async def load(self):
        self.user = await user_service.get_me(bearer_token=self.bearer_token)

