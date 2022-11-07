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

