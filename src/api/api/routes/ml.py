import io
from typing import List, Union, Optional

import pandas as pd
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import StreamingResponse, Response
from starlette.status import HTTP_204_NO_CONTENT

from api.core.config import settings
from api.core.deps import get_session, get_current_user
from api.crud.ml import (
    create_ml_model, get_ml_models, get_ml_model_by_url, get_ml_model_by_name, get_ml_models_by_user, get_predictions,
    get_ml_metrics, get_ml_model, delete_ml_model_by_id, get_latest_ml_metrics, get_latest_model_ml_metrics,
    get_ml_model_rankings
)
from api.crud.result import get_latest_approved_result
from api.crud.user import get_user
from api.models.ml import RowForML, DataForML, MLModelCreate, MLModelRead, MLModel, PredictionRead, MLMetric, \
    MLModelUpdate, MLModelRanking
from api.models.team import UsersForTeamsSuggestion
from api.models.user import User
from api.services.team_suggestion import suggest_most_fair_teams
from api.services.ml import get_ml_data

router = APIRouter()


@router.get("/ml/training_data/csv", response_class=StreamingResponse, tags=["ml"])
async def get_ml_training_data_csv(
    n_rows: Union[int, None] = None,
    session: AsyncSession = Depends(get_session)
):
    ml_data_internal = await get_ml_data(session, n_rows)
    ml_data = DataForML(data = [RowForML(**row.dict()) for row in ml_data_internal.data])
    ml_data_df = pd.DataFrame([row.dict() for row in ml_data.data])
    stream = io.StringIO()

    ml_data_df.to_csv(stream, index=False)
    response = StreamingResponse(
        iter([stream.getvalue()]), media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return response


@router.get("/ml/training_data/json", response_model=DataForML, tags=["ml"])
async def get_ml_training_data_json(
    n_rows: Union[int, None] = None,
    session: AsyncSession = Depends(get_session)
):
    return await get_ml_data(session, n_rows)


@router.get("/ml/example_prediction_data/json", response_model=DataForML, tags=["ml"])
async def get_ml_prediction_data_example_json(
    session: AsyncSession = Depends(get_session)
):
    latest_approved_result = await get_latest_approved_result(session)
    return await get_ml_data(
        session=session,
        n_rows=settings.N_HISTORICAL_ROWS_FOR_PREDICTION + 1,
        result_id_to_predict=latest_approved_result.id,
    )


@router.post("/ml/ml_models/", tags=["ml"])
async def add_ml_model(
    ml_model: MLModelCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    preexisting_model_name = await get_ml_model_by_name(session=session, name=ml_model.model_name)
    if preexisting_model_name:
        raise HTTPException(status_code=400, detail="ML model name already registered. Model name must be unique.")

    preexisting_model_url = await get_ml_model_by_url(session=session, url=ml_model.model_url)
    if preexisting_model_url:
        raise HTTPException(status_code=400, detail="ML model URL already registered. Model URL must be unique.")

    current_user_models = await get_ml_models_by_user(session=session, user_id=current_user.id)
    if len(current_user_models) > 2:
        raise HTTPException(
            status_code=400,
            detail="A user can hve no more than 3 ML models registered. Please edit one of your current models"
        )
    latest_approved_result = await get_latest_approved_result(session)
    if not latest_approved_result:
        raise HTTPException(
            status_code=400,
            detail="No approved result found. At least one result must be approved before a model can be created."
        )
    ml_model = await create_ml_model(session=session, ml_model_create=ml_model, user_id=current_user.id)
    if not ml_model:
        raise HTTPException(
            status_code=400,
            detail=(
                "ML model could not be created. "
                "The model URL does not return prediction when called with example data. "
                "Please make sure that the model URL can make predictions with the example data "
                "available at /ml/example_prediction_data/json."
            )
        )
    return ml_model


@router.get("/ml/ml_models/", response_model=List[MLModelRead], tags=["ml"])
async def read_ml_models(
    session: AsyncSession = Depends(get_session),
):
    return await get_ml_models(session)


@router.get("/ml/ml_models/{id}", response_model=MLModel, tags=["ml"])
async def read_ml_model(
    model_id: int,
    session: AsyncSession = Depends(get_session),
):
    ml_model = await get_ml_model(session, model_id=model_id)
    if not ml_model:
        raise HTTPException(status_code=404, detail="ML model not found")
    return ml_model


@router.get("/ml/ml_models/me/", response_model=List[MLModel], tags=["ml"])
async def read_ml_models_for_user(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await get_ml_models_by_user(session, user_id=current_user.id)


@router.put("/ml/ml_models/{model_id}", response_model=MLModel, tags=["ml"])
async def update_ml_model(
    model_id: int,
    ml_model_update: MLModelUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ml_model = await get_ml_model(session, model_id=model_id)
    if not ml_model:
        raise HTTPException(status_code=404, detail="ML model not found")
    if ml_model.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own ML models")
    if ml_model_update.model_name:
        ml_model.model_name = ml_model_update.model_name
    if ml_model_update.model_url:
        ml_model.model_url = ml_model_update.model_url
    await session.commit()
    await session.refresh(ml_model)
    return ml_model


@router.delete("/ml/ml_models/{model_id}", status_code=HTTP_204_NO_CONTENT, response_class=Response, tags=["ml"])
async def delete_ml_model(
    model_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ml_model = await get_ml_model(session, model_id=model_id)
    if not ml_model:
        raise HTTPException(status_code=404, detail="ML model not found")
    if ml_model.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own ML models")
    await delete_ml_model_by_id(session, model_id=model_id)


@router.post("/ml/suggest_teams/", tags=["ml"])
async def suggest_teams(
    users: UsersForTeamsSuggestion,
    session: AsyncSession = Depends(get_session),
):
    for user_id in [
        users.user_id_1,
        users.user_id_2,
        users.user_id_3,
        users.user_id_4,
    ]:
        if not await get_user(session=session, user_id=user_id):
            raise HTTPException(
                status_code=400, detail="One of the user id's does not exist."
            )

    return await suggest_most_fair_teams(users=users, session=session)


@router.get("/ml/predictions/", response_model=List[PredictionRead], tags=["ml"])
async def read_ml_predictions(
    skip: int = 0,
    limit: int = 100,
    ml_model_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    return await get_predictions(session=session, skip=skip, limit=limit, ml_model_id=ml_model_id)


@router.get("/ml/metrics/", response_model=List[MLMetric], tags=["ml"])
async def read_ml_metrics(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    ml_model_id: Optional[int] = None,
):
    return await get_ml_metrics(session, skip=skip, limit=limit, ml_model_id=ml_model_id)


@router.get("/ml/metrics/latest", response_model=List[MLMetric], tags=["ml"])
async def read_ml_metrics(session: AsyncSession = Depends(get_session)):
    return await get_latest_ml_metrics(session)


@router.get("/ml/rankings/", response_model=List[MLModelRanking], tags=["ml"])
async def read_ml_model_rankings(session: AsyncSession = Depends(get_session),
):
    return await get_ml_model_rankings(session=session)
