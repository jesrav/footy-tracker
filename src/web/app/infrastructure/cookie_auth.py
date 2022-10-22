import hashlib
from typing import Optional, Union

from fastapi import Request
from fastapi import Response

bearer_cookie_name = 'footy_tracker_bearer_token'
user_id_cookie_name = 'footy_tracker_account'


def set_user_id_cookie(response: Response, user_id: int):
    hash_val = hash_text(str(user_id))
    val = "{}:{}".format(user_id, hash_val)
    response.set_cookie(user_id_cookie_name, val, secure=False, httponly=True, samesite='Lax')


def set_bearer_token_cookie(response: Response, bearer_token: str):
    hash_val = hash_text(bearer_token)
    val = "{}:{}".format(bearer_token, hash_val)
    response.set_cookie(bearer_cookie_name, val, secure=False, httponly=True, samesite='Lax')


def get_user_id_via_auth_cookie(request: Request) -> Optional[int]:
    if user_id_cookie_name not in request.cookies:
        return None

    val = request.cookies[user_id_cookie_name]
    parts = val.split(':')
    if len(parts) != 2:
        return None

    user_id = parts[0]
    hash_val = parts[1]
    hash_val_check = hash_text(user_id)
    if hash_val != hash_val_check:
        print("Warning: Hash mismatch, invalid cookie value")
        return None

    return try_int(user_id)


def get_bearer_token_from_cookie(request: Request) -> Union[str, None]:
    if bearer_cookie_name not in request.cookies:
        return None

    val = request.cookies[bearer_cookie_name]
    parts = val.split(':')
    if len(parts) != 2:
        return None

    bearer_token = parts[0]
    hash_val = parts[1]
    hash_val_check = hash_text(bearer_token)
    if hash_val != hash_val_check:
        print("Warning: Hash mismatch, invalid cookie value")
        return None
    return bearer_token


def logout(response: Response):
    response.delete_cookie(bearer_cookie_name)
    response.delete_cookie(user_id_cookie_name)


def try_int(text) -> int:
    try:
        return int(text)
    except:
        return 0


def hash_text(text: str) -> str:
    text = 'salty__' + text + '__text'
    return hashlib.sha512(text.encode('utf-8')).hexdigest()


