from typing import List, Dict

from starlette.requests import Request

from app.models.ml import MLModel, MLModelRead, MLMetric
from app.services import ml_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class MLModelViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.ml_model: MLModel = None
        self.model_ml_metrics: List[MLMetric]
        self.latest_model_ml_metric: MLMetric

    async def load(self):

        user_ml_models = await ml_service.get_user_ml_models(self.bearer_token)
        self.user_ml_models = {i: ml_model for i, ml_model in enumerate(user_ml_models)}

        self.ml_models = await ml_service.get_ml_models()

        ml_metrics = await ml_service.get_ml_metrics()

        for ml_model_id in [m.id for m in self.ml_models]:
            self.model_ml_metrics[ml_model_id] = [metric for metric in ml_metrics if metric.ml_model_id == ml_model_id]
        for model_id in self.model_ml_metrics:
            if self.model_ml_metrics[model_id]:
                self.model_latest_ml_metric[model_id] = sorted(
                    self.model_ml_metrics[model_id], key=lambda x: x.prediction_dt
                )[-1]
            else:
                self.model_latest_ml_metric[model_id] = None
        # Get rank of each model
        model_latest_ml_metric_not_missing = {k: v for k, v in self.model_latest_ml_metric.items() if v is not None}
        model_latest_ml_metric_missing = {k: v for k, v in self.model_latest_ml_metric.items() if v is None}
        for model_id in model_latest_ml_metric_not_missing:
            self.ml_model_rankings[model_id] = 1
            for other_model_id in model_latest_ml_metric_not_missing:
                if model_latest_ml_metric_not_missing[model_id].rolling_short_window_mae > \
                        model_latest_ml_metric_not_missing[other_model_id].rolling_short_window_mae:
                    self.ml_model_rankings[model_id] += 1
        for model_id in model_latest_ml_metric_missing:
            self.ml_model_rankings[model_id] = None