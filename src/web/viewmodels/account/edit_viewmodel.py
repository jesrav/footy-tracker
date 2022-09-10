from typing import Optional, List

from starlette.requests import Request

from models.user import UserRead, UserUpdate
from models.validation_error import ValidationError
from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


class AccountEditViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user: Optional[UserRead] = None
        self.form: Optional[str] = None

    async def post_form(self):
        self.form = await self.request.form()
        self.user: UserRead = await user_service.update_user(
            user_updates=UserUpdate(
                motto=self.form.get('motto'),
                email=self.form.get('email'),
                nickname=self.form.get('nickname'),
            ),
            bearer_token=self.bearer_token,
        )
