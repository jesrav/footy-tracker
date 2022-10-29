from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.ml import MLModel, MLModelCreate, Prediction, PredictionRead, MLMetric


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


async def delete_ml_model_by_id(session: AsyncSession, model_id: int):
    statement = delete(MLModel).filter(MLModel.id == model_id)
    await session.execute(statement)
    await session.commit()


async def add_prediction(
        session: AsyncSession, model_id: int, result_id: int, predicted_goal_diff: float
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


async def get_ml_metrics(session: AsyncSession) -> List[MLMetric]:
    statement = select(MLMetric)
    result = await session.execute(statement)
    return result.scalars().all()


async def add_ml_metrics(ml_metrics: List[MLMetric], session: AsyncSession) -> None:
    existing_ml_metrics = await get_ml_metrics(session=session)
    new_ml_metrics = [m for m in ml_metrics if m.prediction_id not in [m.prediction_id for m in existing_ml_metrics]]
    for ml_metric in new_ml_metrics:
        session.add(ml_metric)
    await session.commit()
