from typing import Optional

from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.infrastructure import cookie_auth
from app.models.validation_error import ValidationError
from app.services import user_service


class ViewModelBase:

    def __init__(self, request: Request):
        self.request: Request = request
        self.error: Optional[str] = None
        self.user_id: Optional[int] = cookie_auth.get_user_id_via_auth_cookie(self.request)
        self.bearer_token: Optional[str] = cookie_auth.get_bearer_token_from_cookie(self.request)
        self.is_logged_in = self.bearer_token is not None
        self.bearer_token_expired = False
        self.redirect_response = None
        self.user = None

    async def authorize(self):
        redirect_response = RedirectResponse('/account/login', status_code=status.HTTP_302_FOUND)
        if not self.is_logged_in:
            self.redirect_response = redirect_response
            return self
        try:
            self.user = await user_service.get_me(bearer_token=self.bearer_token)
        except ValidationError as e:
            if e.status_code == 401:
                cookie_auth.logout(redirect_response)
                self.redirect_response = redirect_response
                return self
            else:
                raise e

    async def to_dict(self) -> dict:
        return self.__dict__
