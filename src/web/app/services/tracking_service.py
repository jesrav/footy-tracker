from typing import List, Optional

import httpx
from httpx import Response

from app.config import settings
from app.models.rankings import UserRanking
from app.models.result import ResultSubmissionCreate, ResultSubmissionRead
from app.models.ratings import UserRating
from app.models.user_stats import UserStats
from app.models.validation_error import ValidationError


async def register_result(result: ResultSubmissionCreate, bearer_token: str) -> ResultSubmissionRead:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(
            url=settings.BASE_WEB_API_URL + "/results/",
            json=result.dict(),
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return ResultSubmissionRead(**resp.json())


async def get_approved_results(skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[ResultSubmissionRead]:
    async with httpx.AsyncClient() as client:
        if user_id:
            url = settings.BASE_WEB_API_URL + f"/results/?for_approval=false&skip={skip}&limit={limit}&user_id={user_id}"
        else:
            url = settings.BASE_WEB_API_URL + f"/results/?for_approval=false&skip={skip}&limit={limit}"
        resp: Response = await client.get(url=url)
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [ResultSubmissionRead(**r) for r in resp.json()]


async def get_results_for_approval_by_user(bearer_token: str) -> List[ResultSubmissionRead]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(
            url=settings.BASE_WEB_API_URL + f"/results_for_approval_by_user/",
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [ResultSubmissionRead(**r) for r in resp.json()]


async def get_results_for_approval_submitted_by_users_team(bearer_token: str) -> List[ResultSubmissionRead]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(
            url=settings.BASE_WEB_API_URL + f"/results_for_approval_submitted_by_users_team/",
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [ResultSubmissionRead(**r) for r in resp.json()]


async def validate_result(result_id: int, approved: bool, bearer_token: str) -> ResultSubmissionRead:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(
            url=settings.BASE_WEB_API_URL + f"/validate_result/{result_id}/?approved={approved}",
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return ResultSubmissionRead(**resp.json())


async def get_user_ratings(user_id: int, skip: int = 0, limit: int = 100) -> List[UserRating]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(
            url=settings.BASE_WEB_API_URL + f"/ratings/{user_id}/?skip={skip}&limit={limit}"
        )
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [UserRating(**r) for r in resp.json()]


async def get_latest_user_rating(user_id: int) -> UserRating:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=settings.BASE_WEB_API_URL + f"/ratings/latest/{user_id}")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return UserRating(**resp.json())


async def get_latest_user_ratings() -> List[UserRating]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=settings.BASE_WEB_API_URL + f"/ratings/latest")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [UserRating(**r) for r in resp.json()]


async def get_user_rankings() -> List[UserRanking]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=settings.BASE_WEB_API_URL + f"/rankings/")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [UserRanking(**r) for r in resp.json()]


async def get_user_stats() -> List[UserStats]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=settings.BASE_WEB_API_URL + f"/user_stats/")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [UserStats(**r) for r in resp.json()]