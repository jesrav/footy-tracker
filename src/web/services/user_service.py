from typing import Optional, List

import httpx
from httpx import Response

from models.user import UserOut
from models.validation_error import ValidationError

BASE_WEB_API_URL = "http://127.0.0.1:8000"


async def create_account(nickname: str, email: str, password: str) -> Optional[UserOut]:
    json_data = {"nickname": nickname, "password": password, "email": email}
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/users/", json=json_data)
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return UserOut(**resp.json())


async def login_user(email: str, password: str) -> Optional[UserOut]:
    json_data = {"password": password, "email": email}
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/users/login/", json=json_data)
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserOut(**resp.json())


async def get_user_by_id(user_id: int) -> UserOut:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/{user_id}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserOut(**resp.json())


async def get_user_by_email(email: str) -> UserOut:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/by_email/{email}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserOut(**resp.json())


async def get_user_by_nickname(nickname: str) -> UserOut:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/by_nickname/{nickname}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserOut(**resp.json())


async def get_all_users() -> List[UserOut]:
    user_limit = 1000
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/?limit{user_limit}")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return [UserOut(**user_dict) for user_dict in resp.json()]
