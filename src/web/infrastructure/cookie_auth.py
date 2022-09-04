import hashlib

from fastapi import Request
from fastapi import Response

auth_cookie_name = 'footy_tracker_bearer_token'


def set_bearer_token_cookie(response: Response, bearer_token: str):
    hash_val = __hash_text(bearer_token)
    val = "{}:{}".format(bearer_token, hash_val)
    response.set_cookie(auth_cookie_name, val, secure=False, httponly=True, samesite='Lax')


def __hash_text(text: str) -> str:
    text = 'salty__' + text + '__text'
    return hashlib.sha512(text.encode('utf-8')).hexdigest()


def get_bearer_token_from_cookie(request: Request):
    if auth_cookie_name not in request.cookies:
        return None

    val = request.cookies[auth_cookie_name]
    parts = val.split(':')
    if len(parts) != 2:
        return None

    bearer_token = parts[0]
    hash_val = parts[1]
    hash_val_check = __hash_text(bearer_token)
    if hash_val != hash_val_check:
        print("Warning: Hash mismatch, invalid cookie value")
        return None
    return bearer_token


def logout(response: Response):
    response.delete_cookie(auth_cookie_name)
