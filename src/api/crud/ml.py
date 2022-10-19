from typing import Optional, List

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlmodel.ext.asyncio.session import AsyncSession

from models.ml import MLModel, MLModelCreate, Prediction, PredictionRead, RollingMAE


async def create_ml_model(
    session: AsyncSession,
        ml_model_create: MLModelCreate,
        user_id: int,
) -> MLModel:
    ml_model = MLModel(
        model_name=ml_model_create.model_name,
        model_url=ml_model_create.model_url,
        user_id=user_id
    )
    session.add(ml_model)
    await session.commit()
    await session.refresh(ml_model)

    return ml_model


async def get_ml_models(session: AsyncSession) -> List[MLModel]:
    statement = select(MLModel)
    result = await session.execute(statement)
    return result.scalars().all()


async def get_ml_models_by_user(session: AsyncSession, user_id: int) -> List[MLModel]:
    statement = select(MLModel).filter(MLModel.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()


async def get_ml_model(session: AsyncSession, model_id: int) -> Optional[MLModel]:
    statement = select(MLModel).filter(MLModel.id == model_id)
    result = await session.execute(statement)
    return result.scalars().first()


async def get_ml_model_by_name(session: AsyncSession, name: str) -> Optional[MLModel]:
    statement = select(MLModel).filter(MLModel.model_name == name)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_ml_model_by_url(session: AsyncSession, url: str) -> Optional[MLModel]:
    statement = select(MLModel).filter(MLModel.model_url == url)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def add_prediction(
        session: AsyncSession, model_id: int, result_id: int, predicted_goal_diff: int
) -> Prediction:
    prediction = Prediction(
        ml_model_id=model_id,
        result_id=result_id,
        predicted_goal_diff=predicted_goal_diff,
    )
    session.add(prediction)
    await session.commit()
    await session.refresh(prediction)
    return prediction


async def get_predictions(session: AsyncSession) -> List[PredictionRead]:
    statement = select(Prediction)
    result = await session.execute(statement.options(joinedload('result'),))
    predictions = result.scalars().all()
    predictions_read = []
    for prediction in predictions:
        predictions_read.append(
            PredictionRead(
                id=prediction.id,
                ml_model_id=prediction.ml_model_id,
                result_id=prediction.result_id,
                predicted_goal_diff=prediction.predicted_goal_diff,
                result_goal_diff=(
                    prediction.result.goals_team1 - prediction.result.goals_team2
                    if prediction.result.approved else None
                ),
                created_dt=prediction.created_dt,
            )
        )
    return predictions_read


def mean_absolute_error(y_pred: float, y_actual: int) -> float:
    return abs(y_pred - y_actual)


def get_ml_metrics(predictions: PredictionRead) -> List[RollingMAE]:
    window = 5
    predictions_df = pd.DataFrame([pred.dict() for pred in predictions])
    predictions_df = predictions_df.sort_values(by=['ml_model_id', 'created_dt'], ascending=False)
    predictions_df['mae'] = predictions_df.apply(lambda x: mean_absolute_error(x['predicted_goal_diff'], x['result_goal_diff']), axis=1)
    predictions_df["rolling_model_mae"] = predictions_df.groupby('ml_model_id')["mae"].rolling(window=window, min_periods=1).mean().reset_index()["mae"]
    return predictions_df
