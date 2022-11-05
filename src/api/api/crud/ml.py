from typing import Optional, List, Union

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.background import BackgroundTasks

from api.core.config import settings
from api.crud.result import get_latest_approved_result
from api.models.ml import MLModel, MLModelCreate, Prediction, PredictionRead, MLMetric, DataForML, RowForML, \
    DataForMLInternal
from api.models.result import ResultSubmission
from api.services.ml import get_ml_prediction, get_ml_data, calculate_ml_metrics


async def create_ml_model(
    session: AsyncSession,
    ml_model_create: MLModelCreate,
    user_id: int,
) -> MLModel:
    # Test that the model url can be used to make predictions
    latest_approved_result = await get_latest_approved_result(session)
    data_for_test_prediction = await get_ml_data(
        session=session,
        n_rows=settings.N_HISTORICAL_ROWS_FOR_PREDICTION + 1,
        result_id_to_predict=latest_approved_result.id,
    )
    test_prediction = await get_ml_prediction(
        url=ml_model_create.model_url,
        data_for_prediction=DataForML(data=[RowForML(**r.dict()) for r in data_for_test_prediction.data])
    )
    if test_prediction is None:
        return None

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
    return [
        PredictionRead(
            id=prediction.id,
            ml_model_id=prediction.ml_model_id,
            result_id=prediction.result_id,
            predicted_goal_diff=prediction.predicted_goal_diff,
            result_goal_diff=(
                prediction.result.goals_team1 - prediction.result.goals_team2
                if prediction.result.approved
                else None
            ),
            created_dt=prediction.created_dt,
        )
        for prediction in predictions
    ]


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


async def add_prediction_background_tasks(
        result: ResultSubmission, ml_prediction_background_tasks: BackgroundTasks, session: AsyncSession
):
    """Add predictions tasks for a specific result to a collection of background tasks `ml_prediction_background_tasks`

    A prediction task is added for each model registered in the db.
    """
    ml_models = await get_ml_models(session=session)
    ml_data = await get_ml_data(
        session=session, n_rows=settings.N_HISTORICAL_ROWS_FOR_PREDICTION, result_id_to_predict=result.id
    )
    for ml_model in ml_models:
        ml_prediction_background_tasks.add_task(
            single_prediction_task,
            result_id=result.id,
            ml_model=ml_model,
            ml_data=ml_data,
            session=session,
        )


async def update_ml_metrics_from_predictions(session: AsyncSession):
    """Add model metrics for any new approved results"""
    predictions = await get_predictions(session=session)
    ml_metrics = calculate_ml_metrics(
        predictions,
        short_rolling_window_size=settings.METRICS_SHORT_WINDOW_SIZE,
        long_rolling_window_size=settings.METRICS_LONG_WINDOW_SIZE
    )
    await add_ml_metrics(ml_metrics, session=session)


async def single_prediction_task(
    result_id: int,
    ml_model: MLModel,
    ml_data: DataForMLInternal,
    session: AsyncSession,
) -> Union[Prediction, None]:
    """Make prediction for a specific result id using an ML model API and write prediction to db.

    If the API call is unsuccessful we return None and no prediction is written to the db.


    Parameters
    ----------
    result_id: int
        Result id for the match we are making a prediction for
    ml_model: MLModel
        ML model (API) we are using to make the prediction
    ml_data: DataForMLInternal
        Data for making prediction. Contains information that is not sent to the ML API
    session: AsyncSession

    Returns
    -------
    int
        Predicted goal difference (team1 goals - team2 goals)
    """
    # Get data for prediction, without columns we don't want to send to the ML endpoint
    data_for_prediction = DataForML.parse_obj(ml_data)

    # Get a prediction from ML model API
    prediction = await get_ml_prediction(url=ml_model.model_url, data_for_prediction=data_for_prediction)

    if prediction is None:
        return None

    # Get the row/result that the prediction was made on
    row_to_predict = [r for r in ml_data.data if r.result_to_predict][0]

    # If the teams have been switched (not shown to the API), we correct the prediction
    if row_to_predict.teams_switched:
        prediction = -prediction

    # Add prediction to db
    prediction = await add_prediction(
        session=session, model_id=ml_model.id, result_id=result_id, predicted_goal_diff=prediction
    )
    return prediction
