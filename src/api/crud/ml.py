from typing import Optional, List

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.ml import MLModel, MLModelCreate, Prediction, DataForMLInternal, DataForML
from services.ml import get_ml_prediction


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


async def single_prediction_task(
    result_id: int,
    ml_model: MLModel,
    ml_data: DataForMLInternal,
    session: AsyncSession,
):
    """Make prediction and register prediction using an ML model API"""

    # Get data for prediction, without columns we don't want to send to the ML endpoint
    data_for_prediction = DataForML.parse_obj(ml_data)
    prediction = await get_ml_prediction(url=ml_model.model_url, data_for_prediction=data_for_prediction)

    if not prediction:
        return None

    # Get the row that the prediction is to be used on
    row_to_predict = [r for r in ml_data.data if r.result_to_predict][0]
    # If the teams have been switched (not shown to the algorithm), we correct the prediction
    if row_to_predict.teams_switched:
        prediction = -prediction

    # Add prediction to db
    prediction = await add_prediction(
        session=session, model_id=ml_model.id, result_id=result_id, predicted_goal_diff=prediction
    )
    return prediction
