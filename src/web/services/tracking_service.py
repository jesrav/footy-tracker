from typing import List

import httpx
from httpx import Response

from models.result import ResultSubmissionCreate, ResultSubmissionOut
from models.validation_error import ValidationError

BASE_WEB_API_URL = "http://127.0.0.1:8000"


async def register_result(result: ResultSubmissionCreate) -> ResultSubmissionOut:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(url=BASE_WEB_API_URL + "/results/", json=result.dict())
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return ResultSubmissionOut(**resp.json())


async def get_results_for_approval(user_id: int) -> List[ResultSubmissionOut]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=BASE_WEB_API_URL + f"/users/{user_id}/results_for_approval/")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [ResultSubmissionOut(**r) for r in resp.json()]
