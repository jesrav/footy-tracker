from typing import List

from starlette.requests import Request

from app.models.ml import MLModel, MLModelRead
from app.models.result import ResultForUserDisplay
from app.services import ml_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class MLViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user_ml_models: List[MLModel] = []
        self.ml_models: List[MLModelRead] = []

    async def load(self):
        self.user_ml_models = await ml_service.get_user_ml_models(self.bearer_token)
        self.ml_models = await ml_service.get_ml_models()
        