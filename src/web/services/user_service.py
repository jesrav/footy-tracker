import os
from typing import Optional, List

import httpx
from httpx import Response

from models.user import UserRead, UserUpdate
from models.validation_error import ValidationError

BASE_WEB_API_URL = os.environ.get("API_URL")


async def create_account(nickname: str, email: str, password: str) -> Optional[UserRead]:
    json_data = {"nickname": nickname, "password": password, "email": email}
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/users/", json=json_data)
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return UserRead(**resp.json())


async def login_user(email: str, password: str) -> Optional[UserRead]:
    json_data = {"password": password, "email": email}
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/users/login/", json=json_data)
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserRead(**resp.json())


async def get_user_by_id(user_id: int) -> UserRead:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/{user_id}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserRead(**resp.json())


async def get_user_by_email(email: str) -> UserRead:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/by_email/{email}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserRead(**resp.json())


async def get_user_by_nickname(nickname: str) -> UserRead:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/by_nickname/{nickname}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserRead(**resp.json())


async def get_all_users() -> List[UserRead]:
    user_limit = 1000
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/?limit{user_limit}")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return [UserRead(**user_dict) for user_dict in resp.json()]


async def update_user(user_id: int, user_updates: UserUpdate) -> Optional[UserRead]:
    json_data = {
        "nickname": user_updates.nickname,
        "password": user_updates.password,
        "email": user_updates.email,
        "motto": user_updates.motto,
        "profile_pic_path": user_updates.profile_pic_path,
    }
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + f"/users/{user_id}/update/", json=json_data)
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return UserRead(**resp.json())
