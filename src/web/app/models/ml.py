from datetime import datetime
from typing import Optional

from pydantic import BaseModel, AnyHttpUrl


class MLModelCreate(BaseModel):
    model_name: str
    model_url: AnyHttpUrl


class MLModel(MLModelCreate):
    id: int
    user_id: int
    created_dt: datetime


class MLModelRead(BaseModel):
    id: int
    model_name: str
    user_id: int
    created_dt: datetime


class MLMetric(BaseModel):
    id: int
    prediction_id: int
    result_id: int
    ml_model_id: int
    prediction_dt: datetime
    result_goal_diff: int
    predicted_goal_diff: Optional[float]
    rolling_short_window_mae: float
    rolling_long_window_mae: float
    rolling_short_window_bias: float
    rolling_long_window_bias: float


class MLModelRanking(BaseModel):
    ml_model_id: int
    ranking: int
