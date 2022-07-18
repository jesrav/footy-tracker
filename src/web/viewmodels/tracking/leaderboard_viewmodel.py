from starlette.requests import Request

from src.web.viewmodels.shared.viewmodel import ViewModelBase


class LeaderboardViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)

