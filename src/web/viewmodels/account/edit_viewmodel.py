from typing import Optional, List

from starlette.requests import Request

from models.user import UserRead, UserUpdate
from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


class AccountEditViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user: Optional[UserRead] = None
        self.form: Optional[str] = None

    async def load(self):
        self.user = await user_service.get_user_by_id(self.user_id)

    async def load_form(self):
        self.form = await self.request.form()
        self.user: UserRead = await user_service.update_user(
            user_id=self.user_id,
            user_updates=UserUpdate(
                motto=self.form.get('motto'),
                email=self.form.get('email'),
                nickname=self.form.get('nickname'),
            )
        )
