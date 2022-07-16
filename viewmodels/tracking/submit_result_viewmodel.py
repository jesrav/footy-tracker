from starlette.requests import Request

from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


class SubmitResultViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)

        self.users = user_service.get_all_users()
