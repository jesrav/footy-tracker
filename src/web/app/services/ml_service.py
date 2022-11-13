from typing import List, Optional

import httpx
from httpx import Response

from app.models.ml import MLModelRead, MLModel, MLModelCreate, MLMetric, MLModelRanking, PredictionRead
from app.models.team import UsersForTeamsSuggestion, TeamsSuggestion
from app.models.validation_error import ValidationError
from app.config import settings


async def get_teams_suggestion(
        users: UsersForTeamsSuggestion, bearer_token: str
) -> TeamsSuggestion:
    timeout = httpx.Timeout(20)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp: Response = await client.post(
            url=f"{settings.BASE_WEB_API_URL}/ml/suggest_teams/",
            json=users.dict(), headers={"Authorization": f"Bearer {bearer_token}"}
        )

        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return TeamsSuggestion(**resp.json())


async def add_ml_model(ml_model: MLModelCreate, bearer_token: str) -> MLModel:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(
            url=f"{settings.BASE_WEB_API_URL}/ml/ml_models/",
            json=ml_model.dict(),
            headers={"Authorization": f"Bearer {bearer_token}"}
        )

        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return MLModel(**resp.json())


async def get_ml_models() -> List[MLModelRead]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=f"{settings.BASE_WEB_API_URL}/ml/ml_models/")

        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [MLModelRead(**m) for m in resp.json()]


async def get_user_ml_models(bearer_token: str) -> List[MLModel]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(
            url=f"{settings.BASE_WEB_API_URL}/ml/ml_models/me/",
            headers={"Authorization": f"Bearer {bearer_token}"}
        )

        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [MLModel(**m) for m in resp.json()]


async def get_ml_model_predictions(ml_model_id: int) -> List[PredictionRead]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(
            url=f"{settings.BASE_WEB_API_URL}/ml/predictions/?ml_model_id={ml_model_id}"
        )

        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [PredictionRead(**m) for m in resp.json()]


async def get_ml_metrics(ml_model_id: int) -> List[MLMetric]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(
            url=f"{settings.BASE_WEB_API_URL}/ml/metrics/?ml_model_id={ml_model_id}"
        )

        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [MLMetric(**m) for m in resp.json()]


async def get_latest_ml_metrics() -> List[MLMetric]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=f"{settings.BASE_WEB_API_URL}/ml/metrics/latest")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [MLMetric(**m) for m in resp.json()]


async def get_ml_model_rankings() -> List[MLModelRanking]:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url=f"{settings.BASE_WEB_API_URL}/ml/rankings/")
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return [MLModelRanking(**m) for m in resp.json()]
