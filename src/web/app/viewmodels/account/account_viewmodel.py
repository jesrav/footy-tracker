from typing import Optional

from starlette.requests import Request

from app.models.user import UserRead
from app.viewmodels.shared.viewmodel import ViewModelBase


class AccountViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user: Optional[UserRead] = None




