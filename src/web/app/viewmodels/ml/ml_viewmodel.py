from typing import List, Dict

from starlette.requests import Request

from app.models.ml import MLModel, MLModelRead, MLMetric
from app.services import ml_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class MLViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user_ml_models: Dict[int, MLModel] = {}
        self.ml_models: List[MLModelRead] = []
        self.model_ml_metrics: Dict[int, List[MLMetric]] = {}
        self.model_latest_ml_metric: Dict[int, MLMetric] = {}
        self.model_css_ids = ["model-1", "model-2", "model-3"]

    async def load(self):
        user_ml_models = await ml_service.get_user_ml_models(self.bearer_token)
        self.user_ml_models = {i: ml_model for i, ml_model in enumerate(user_ml_models)}
        self.ml_models = await ml_service.get_ml_models()
        ml_metrics = await ml_service.get_ml_metrics()
        for ml_model_id in [m.id for m in self.ml_models]:
            self.model_ml_metrics[ml_model_id] = [metric for metric in ml_metrics if metric.ml_model_id == ml_model_id]
        for model_id in self.model_ml_metrics:
            self.model_latest_ml_metric[model_id] = sorted(
                self.model_ml_metrics[model_id], key=lambda x: x.prediction_dt
            )[-1]
