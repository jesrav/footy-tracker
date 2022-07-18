from typing import Optional

from starlette.requests import Request

from src.web.services import user_service
from src.web.viewmodels.shared.viewmodel import ViewModelBase


class RegisterViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)

        self.nickname: Optional[str] = None
        self.password: Optional[str] = None
        self.email: Optional[str] = None

    async def load(self):
        form = await self.request.form()
        self.nickname = form.get('nickname')
        self.password = form.get('password')
        self.email = form.get('email')

        if not self.nickname or not self.nickname.strip():
            self.error = "Your name is required."
        elif not self.email or not self.email.strip():
            self.error = "Your email is required."
        elif not self.password:
            self.error = "Your password is required."
        elif len(self.password) < 8:
            self.error = "Your password must be at 8 characters."
        elif user_service.get_user_by_nickname(self.nickname):
            self.error = "That nickname is already taken."
        elif user_service.get_user_by_email(self.email):
            self.error = "That email is already taken. Log in instead?"
