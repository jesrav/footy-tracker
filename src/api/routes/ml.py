import io
from typing import List, Union

from fastapi import Depends, APIRouter, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import StreamingResponse

from core import deps
from core.config import settings
from crud.ml import (
    create_ml_model, get_ml_models, get_ml_model_by_url, get_ml_model_by_name, get_ml_models_by_user, get_predictions,
    get_ml_metrics
)
from core.deps import get_session
from crud.result import get_latest_approve_result
from crud.user import get_user
from models.ml import RowForML, DataForML, MLModelCreate, MLModelRead, MLModel, PredictionRead
from models.team import UsersForTeamsSuggestion
from models.user import User
from services.ml import suggest_most_fair_teams

router = APIRouter()


@router.get("/ml/training_data/csv", response_class=StreamingResponse, tags=["ml"])
async def get_ml_training_data_csv(
    n_rows: Union[int, None] = None,
    session: AsyncSession = Depends(get_session)
):
    results_with_features_df = await get_ml_data(session, n_rows)
    stream = io.StringIO()

    results_with_features_df.to_csv(stream, index=False)
    response = StreamingResponse(
        iter([stream.getvalue()]), media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return response


@router.get("/ml/training_data/json", response_model=List[RowForML], tags=["ml"])
async def get_ml_training_data_json(
    n_rows: Union[int, None] = None,
    session: AsyncSession = Depends(get_session)
):
    results_with_features_df = await get_ml_data(session, n_rows)
    return results_with_features_df.to_dict('records')


@router.get("/ml/example_prediction_data/json", response_model=DataForML, tags=["ml"])
async def get_ml_prediction_data_example_json(
    session: AsyncSession = Depends(get_session)
):
    latest_approved_result= await get_latest_approve_result(session)
    results_with_features_df = await get_ml_data(
        session=session,
        n_rows=settings.N_HISTORICAL_ROWS_FOR_PREDICTION + 1,
        result_id_to_predict=latest_approved_result.id
    )
    return {
        "data": results_with_features_df.to_dict(orient='records')
    }


@router.post("/ml/ml_models/", response_model=MLModelRead, tags=["ml"])
async def add_ml_model(
    ml_model: MLModelCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
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
    ml_model = await create_ml_model(session=session, ml_model_create=ml_model, user_id=current_user.id)
    return ml_model


@router.get("/ml/ml_models/", response_model=List[MLModelRead], tags=["ml"])
async def read_ml_models(
    session: AsyncSession = Depends(get_session),
):
    return await get_ml_models(session)


@router.get("/ml/ml_models/me", response_model=List[MLModel], tags=["ml"])
async def read_ml_models_for_user(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
):
    return await get_ml_models_by_user(session, user_id=current_user.id)


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
                status_code=400, detail=f"One of the user id's does not exist."
            )
    return await suggest_most_fair_teams(users=users, session=session)


@router.get("/ml/predictions/", response_model=List[PredictionRead], tags=["ml"])
async def read_ml_predictions(
    session: AsyncSession = Depends(get_session),
):
    predictions =  await get_predictions(session)
    test = get_ml_metrics(predictions)
    return test
