from typing import List, Optional, Dict

from starlette.requests import Request

from app.models.ml import MLModel, MLMetric, MLModelRanking, PredictionRead
from app.models.result import ResultForUserDisplay
from app.models.user import UserReadUnauthorized
from app.services import ml_service, user_service, tracking_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class MLModelViewModel(ViewModelBase):
    def __init__(self, ml_model_id: int, request: Request):
        super().__init__(request)
        self.ml_model_id = ml_model_id
        self.ml_model: Optional[MLModel] = None
        self.model_user: Optional[UserReadUnauthorized] = None
        self.model_ml_metrics: List[MLMetric] = []
        self.latest_model_ml_metric: Optional[MLMetric] = None
        self.ml_model_ranking: Optional[MLModelRanking] = None
        self.result_dict: Dict[int, ResultForUserDisplay] = {}

    async def load(self):
        ml_models = await ml_service.get_ml_models()
        if self.ml_model_id in [m.id for m in ml_models]:
            self.ml_model = [m for m in ml_models if m.id == self.ml_model_id][0]
        else:
            self.error = "Model not found"

        self.model_user = await user_service.get_user_by_id(self.ml_model.user_id)
        self.model_ml_metrics = await ml_service.get_ml_metrics(self.ml_model.id)

        latest_ml_metric = await ml_service.get_latest_ml_metrics()
        if self.ml_model_id in [m.ml_model_id for m in latest_ml_metric]:
            self.latest_model_ml_metric = [m for m in latest_ml_metric if m.ml_model_id == self.ml_model_id][0]
        else:
            self.latest_model_ml_metric = None

        ml_model_rankings = await ml_service.get_ml_model_rankings()
        if self.ml_model_id in [m.ml_model_id for m in ml_model_rankings]:
            self.ml_model_ranking = [m for m in ml_model_rankings if m.ml_model_id == self.ml_model_id][0]

        results = await tracking_service.get_approved_results()
        self.result_dict = {
            r.id: r for r in results
        }