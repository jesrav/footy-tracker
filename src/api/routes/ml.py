import io
from typing import List, Union

from fastapi import Depends, APIRouter, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import StreamingResponse

from core import deps
from core.config import settings
from crud.ml import (
    get_ml_data, create_ml_model, get_ml_models, get_ml_model_by_url, get_ml_model_by_name, create_user_ml_model
)
from core.deps import get_session
from crud.result import get_latest_approve_result
from models.ml import RowForML, DataForML, MLModelCreate, MLModelRead
from models.user import User

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
    ml_model = await create_ml_model(session=session, ml_model_create=ml_model, commit_changes=False)
    _ = await create_user_ml_model(
        session=session, user_id=current_user.id, ml_model_id=ml_model.id, commit_changes=False
    )
    await session.commit()
    await session.refresh(ml_model)
    return ml_model


@router.get("/ml/ml_models/", response_model=List[MLModelRead], tags=["ml"])
async def read_ml_models(
    session: AsyncSession = Depends(get_session),
):
    return await get_ml_models(session)
