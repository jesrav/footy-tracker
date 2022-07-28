from typing import Optional, List

from starlette.requests import Request

from models.user import UserOut
from models.result import ResultSubmissionOut, ResultForUserValidation
from services import user_service, tracking_service
from viewmodels.shared.viewmodel import ViewModelBase


class AccountViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user: Optional[UserOut] = None
        self.results_to_approve: List[ResultSubmissionOut] = []
        self.result_id: Optional[int] = None
        self.approved: Optional[bool] = None

    async def load(self):
        self.user = await user_service.get_user_by_id(self.user_id)
        results_to_approve = await tracking_service.get_results_for_approval(self.user_id)
        self.results_to_approve = [
            ResultForUserValidation.from_result_submission(
                user_id=self.user_id,
                result=r,
            ) for r in results_to_approve
        ]


    async def load_form(self):
        form = await self.request.form()
        self.result_id = int(form.get('result_id'))
        if form.get('approved') == "false":
            self.approved = False
        if form.get('approved') == "true":
            self.approved = True
