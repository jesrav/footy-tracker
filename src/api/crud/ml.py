from typing import Optional, List

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.ml import MLModel, MLModelCreate, Prediction


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
