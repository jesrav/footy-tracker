import json

import httpx
from httpx import Response

from models.ml_data import DataForML


async def get_ml_prediction(url: str, data_for_ml: DataForML) -> int:
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(
            url=url,
            json=json.loads(data_for_ml.json()),
        )
    return resp.json()