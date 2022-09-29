import json
from typing import Union

import httpx
from httpx import Response

from models.ml import DataForML


async def get_ml_prediction(url: str, data_for_prediction: DataForML) -> Union[int, None]:
    """Get prediction from ml microservice

    If we do not get a response with a status code 200, where the json content is an integer,
    we return None
    """
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(
            url=url,
            json=json.loads(data_for_prediction.json()),
        )

    if resp.status_code == 200:
        json_resp = resp.json()
        if isinstance(json_resp, int):
            return json_resp
    else:
        return None
