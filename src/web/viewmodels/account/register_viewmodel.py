from typing import Optional
import ast

from starlette.requests import Request

from models.validation_error import ValidationError
from services import user_service
from viewmodels.shared.viewmodel import ViewModelBase


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
        else:
            # Try to create the account and catch any errors, such as nickname already used
            try:
                _ = await user_service.create_account(self.nickname, self.email, self.password)
            except ValidationError as e:
                self.error = ast.literal_eval(e.error_msg)["detail"]

            # If a user is logged in without any errors, we log in
            if not self.error:
                self.bearer_token = await user_service.login_user(self.email, self.password)
