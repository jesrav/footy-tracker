from typing import Optional, List

from starlette.requests import Request

from models.user import UserOut
from models.result import ResultSubmissionOut
from services import user_service, tracking_service
from viewmodels.shared.viewmodel import ViewModelBase


class AccountViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user: Optional[UserOut] = None
        self.results_to_approve: List[ResultSubmissionOut] = []

    async def load(self):
        self.user = await user_service.get_user_by_id(self.user_id)
        self.results_to_approve = await tracking_service.get_results_for_approval(self.user_id)

