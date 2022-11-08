from typing import List, Dict

from starlette.requests import Request

from app.models.ml import MLModel, MLMetric
from app.models.user import UserReadUnauthorized
from app.services import ml_service
from app.services import user_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class UserMLOverviewViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.users: Dict[int, UserReadUnauthorized] = {}
        self.user_ml_models: Dict[int, MLModel] = {}
        self.ml_models: Dict[int, MLModel] = {}
        self.model_ml_metrics: Dict[int, List[MLMetric]] = {}
        self.latest_ml_model_metrics: Dict[int, MLMetric] = {}
        self.model_css_ids: List[str] = ["model-1", "model-2", "model-3"]
        self.ml_model_rankings: Dict[int: int] = {}

    async def load(self):
        users = await user_service.get_all_users()
        self.users = {u.id: u for u in users}

        self.user_ml_models = {
            i: ml_model
            for i, ml_model in enumerate(await ml_service.get_user_ml_models(self.bearer_token))
        }
        ml_models = await ml_service.get_ml_models()
        self.ml_models = {
            ml_model.id: ml_model
            for ml_model in ml_models
        }
        self.model_ml_metrics = {
            ml_model.id: await ml_service.get_ml_metrics(ml_model_id=ml_model.id)
            for ml_model in self.user_ml_models.values()
        }
        self.latest_ml_model_metrics = {m.ml_model_id: m for m in await ml_service.get_latest_ml_metrics()}
        self.ml_model_rankings = {mr.ml_model_id: mr for mr in await ml_service.get_ml_model_rankings()}
