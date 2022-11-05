from datetime import datetime

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
