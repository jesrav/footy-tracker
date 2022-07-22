from typing import Optional

import httpx
from httpx import Response

from models.match import MatchBase, Match
from models.user import User
from models.validation_error import ValidationError

BASE_WEB_API_URL = "http://127.0.0.1:8000"


async def register_match(match: MatchBase) -> Match:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/matches/", json=match.dict())
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return Match(**resp.json())


