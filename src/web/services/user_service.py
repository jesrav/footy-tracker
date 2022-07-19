from typing import Optional, List

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
import httpx
from httpx import Response

from models.validation_error import ValidationError

BASE_WEB_API_URL = "http://127.0.0.1:8000"


async def create_account(nickname: str, email: str, password: str):
    json_data = {"nickname": nickname, "password": password, "email": email}
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/users/", json=json_data)
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)

    return resp.json()


# def login_user(email: str, password: str) -> Optional[User]:
#     session = db_session.create_session()
#
#     try:
#         user = session.query(User).filter(User.email == email).first()
#         if not user:
#             return user
#
#         if not crypto.verify(password, user.hash_password):
#             return None
#
#         return user
#     finally:
#         session.close()


async def get_user_by_id(user_id: int):
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/{user_id}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return resp.json()


async def get_user_by_email(email: str):
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/by_email/{email}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return resp.json()


async def get_user_by_nickname(nickname: str):
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/by_nickname/{nickname}")
        if resp.status_code == 404:
            return None
        elif resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        else:
            return resp.json()


# def get_user_by_email(email: str) -> Optional[User]:
#     session = db_session.create_session()
#
#     try:
#         return session.query(User).filter(User.email == email).first()
#     finally:
#         session.close()
#
#
# def get_user_by_nickname(nickname: str) -> Optional[User]:
#     session = db_session.create_session()
#
#     try:
#         return session.query(User).filter(User.nickname == nickname).first()
#     finally:
#         session.close()
#
#
# def get_all_users() -> List[User]:
#     session = db_session.create_session()
#     try:
#         return session.query(User).all()
#     finally:
#         session.close()