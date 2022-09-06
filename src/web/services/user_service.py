import os
from typing import Optional, List, Any, Union

import httpx
from httpx import Response

from models.user import UserRead, UserReadUnauthorized, UserUpdate
from models.validation_error import ValidationError

BASE_WEB_API_URL = os.environ.get("API_URL")


async def create_account(nickname: str, email: str, password: str) -> Optional[UserRead]:
    json_data = {"nickname": nickname, "password": password, "email": email}
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/auth/signin", json=json_data)
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return UserRead(**resp.json())


async def login_user(email: str, password: str) -> Any:
    data = {"password": password, "username": email}
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/auth/login", data=data)
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return resp.json()


async def get_me(bearer_token: str) -> Union[UserRead, None]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(
            url=BASE_WEB_API_URL + f"/me",
            headers={"Authorization": f"Bearer {bearer_token}"}
        )
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserRead(**resp.json())


async def update_user(user_updates: UserUpdate, bearer_token: str) -> Optional[UserRead]:
    json_data = {
        "nickname": user_updates.nickname,
        "password": user_updates.password,
        "email": user_updates.email,
        "motto": user_updates.motto,
        "profile_pic_path": user_updates.profile_pic_path,
    }
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(
            url=BASE_WEB_API_URL + f"/me/update/",
            json=json_data,
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return UserRead(**resp.json())


async def get_user_by_id(user_id: int) -> Union[UserReadUnauthorized, None]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/{user_id}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return UserReadUnauthorized(**resp.json())


async def get_all_users() -> List[UserReadUnauthorized]:
    user_limit = 1000
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/?limit{user_limit}")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return [UserReadUnauthorized(**user_dict) for user_dict in resp.json()]
