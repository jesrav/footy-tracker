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
        self.model_css_ids: List[str] = ["model-1", "model-2", "model-3"]
        self.ml_model_rankings: Dict[int: int] = {}

    async def load(self):
        # Get the users models in a dictionary for convenience
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

        # Get rank of each model
        for model_id in self.model_latest_ml_metric:
            self.ml_model_rankings[model_id] = 1
            for other_model_id in self.model_latest_ml_metric:
                if self.model_latest_ml_metric[model_id].rolling_short_window_mae > \
                        self.model_latest_ml_metric[other_model_id].rolling_short_window_mae:
                    self.ml_model_rankings[model_id] += 1
