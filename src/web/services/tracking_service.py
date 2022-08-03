import os
from typing import List

import httpx
from httpx import Response

from models.result import ResultSubmissionCreate, ResultSubmissionRead
from models.ratings import UserRating
from models.validation_error import ValidationError

BASE_WEB_API_URL = os.environ.get("API_URL")


async def register_result(result: ResultSubmissionCreate) -> ResultSubmissionRead:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/results/", json=result.dict())
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
        print(resp.json())
    return ResultSubmissionRead(**resp.json())


async def get_results_for_approval(user_id: int) -> List[ResultSubmissionRead]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/{user_id}/results_for_approval/")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [ResultSubmissionRead(**r) for r in resp.json()]


async def validate_result(validator_id: int, result_id: int, approved: bool) -> ResultSubmissionRead:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(
            url=BASE_WEB_API_URL + f"/users/{validator_id}/validate_result/{result_id}/?approved={approved}"
        )
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return ResultSubmissionRead(**resp.json())


async def get_latest_user_rating(user_id: int) -> UserRating:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/ratings/{user_id}/latest")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return UserRating(**resp.json())
