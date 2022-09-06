from typing import Optional

from starlette.requests import Request

from infrastructure import cookie_auth


class ViewModelBase:

    def __init__(self, request: Request):
        self.request: Request = request
        self.error: Optional[str] = None
        self.bearer_token: Optional[str] = cookie_auth.get_bearer_token_from_cookie(self.request)
        if self.bearer_token:
            self.user: Optional[str] = cookie_auth.get_bearer_token_from_cookie(self.request)
        self.is_logged_in = self.bearer_token is not None

    def to_dict(self) -> dict:
        return self.__dict__
