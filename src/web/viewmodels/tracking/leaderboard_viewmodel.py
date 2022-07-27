from starlette.requests import Request

from viewmodels.shared.viewmodel import ViewModelBase


class LeaderboardViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)

    async def load_form(self):
        self.form = await self.request.form()
