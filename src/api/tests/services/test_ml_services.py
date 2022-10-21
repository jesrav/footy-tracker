from typing import List

import pytest

from api.models.ml import PredictionRead, MLMetric
from api.services.ml import mean_absolute_error, calculate_ml_metrics


@pytest.mark.parametrize("y_true, y_pred, expected_mae", [(1, 4, 3), (10, 2, 8), (1, 1, 0), (1, 5, 4), (3, 1, 2)])
def test_mean_absolute_error(y_true, y_pred, expected_mae):
    assert mean_absolute_error(y_true, y_pred) == expected_mae


def test_calculate_ml_metrics():
    """Test the calculation of ml metrics"""
    predictions = [
        PredictionRead(id=1, ml_model_id=1, result_id=1, predicted_goal_diff=8, result_goal_diff=5, created_dt="2022-01-01 12:00"),
        PredictionRead(id=2, ml_model_id=1, result_id=2, predicted_goal_diff=7, result_goal_diff=5, created_dt="2022-01-01 12:01"),
        PredictionRead(id=3, ml_model_id=1, result_id=3, predicted_goal_diff=4, result_goal_diff=2, created_dt="2022-01-01 12:02"),
        PredictionRead(id=4, ml_model_id=1, result_id=4, predicted_goal_diff=4, result_goal_diff=1, created_dt="2022-01-01 12:03"),
        PredictionRead(id=5, ml_model_id=1, result_id=5, predicted_goal_diff=4, result_goal_diff=1, created_dt="2022-01-01 12:04"),
        PredictionRead(id=6, ml_model_id=2, result_id=1, predicted_goal_diff=8, result_goal_diff=5, created_dt="2022-01-01 12:05"),
        PredictionRead(id=7, ml_model_id=2, result_id=2, predicted_goal_diff=7, result_goal_diff=5, created_dt="2022-01-01 12:06"),
        PredictionRead(id=8, ml_model_id=2, result_id=3, predicted_goal_diff=4, result_goal_diff=2, created_dt="2022-01-01 12:07"),
        PredictionRead(id=9, ml_model_id=2, result_id=4, predicted_goal_diff=4, result_goal_diff=1, created_dt="2022-01-01 12:08"),
        PredictionRead(id=10, ml_model_id=2, result_id=5, predicted_goal_diff=4, result_goal_diff=1, created_dt="2022-01-01 12:09"),
    ]

    def get_ml_metric(ml_metrics_list: List[MLMetric], prediction_id: int, model_id: int) -> MLMetric:
        return next(m for m in ml_metrics_list if m.prediction_id == prediction_id and m.ml_model_id == model_id)

    ml_metrics = calculate_ml_metrics(predictions, short_rolling_window_size=2, long_rolling_window_size=4)
    assert get_ml_metric(ml_metrics, 1, 1).rolling_short_window_mae == 3, "rolling short window mae not as expected"
    assert get_ml_metric(ml_metrics, 1, 1).rolling_long_window_mae == 3, "rolling long window mae not as expected"
    assert get_ml_metric(ml_metrics, 2, 1).rolling_short_window_mae == 2.5, "rolling short window mae not as expected"
    assert get_ml_metric(ml_metrics, 2, 1).rolling_long_window_mae == 2.5, "rolling long window mae not as expected"
    assert get_ml_metric(ml_metrics, 3, 1).rolling_short_window_mae == 2, "rolling short window mae not as expected"
    assert get_ml_metric(ml_metrics, 3, 1).rolling_long_window_mae == pytest.approx(2.33333, 0.00001), "rolling long window mae not as expected"
    assert get_ml_metric(ml_metrics, 4, 1).rolling_short_window_mae == 2.5, "rolling short window mae not as expected"
    assert get_ml_metric(ml_metrics, 4, 1).rolling_long_window_mae == 2.5, "rolling long window mae not as expected"
    assert get_ml_metric(ml_metrics, 5, 1).rolling_short_window_mae == 3, "rolling short window mae not as expected"
    assert get_ml_metric(ml_metrics, 5, 1).rolling_long_window_mae == 2.5, "rolling long window mae not as expected"