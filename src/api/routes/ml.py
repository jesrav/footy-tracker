import io
from typing import List, Union

from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import StreamingResponse

from crud.ml_training_data import get_ml_data
from core.deps import get_session
from models.ml_data import ColumnsForML

router = APIRouter()


N_HISTORICAL_ROWS_FOR_PREDICION = 100


@router.get("/ml/training_data/csv", response_class=StreamingResponse, tags=["ml"])
async def read_results(
    n_rows: Union[int, None] = None,
    session: AsyncSession = Depends(get_session)
):
    results_with_features_df = await get_ml_data(session, n_rows)
    stream = io.StringIO()

    results_with_features_df.to_csv(stream, index=False)
    response = StreamingResponse(
        iter([stream.getvalue()]),
         media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return response


@router.get("/ml/training_data/json", response_model=List[ColumnsForML], tags=["ml"])
async def read_results(
    n_rows: Union[int, None] = None,
    session: AsyncSession = Depends(get_session)
):
    results_with_features_df = await get_ml_data(session, n_rows)
    return results_with_features_df.to_dict('records')


@router.get("/ml/example_prediction_data/json", response_model=List[ColumnsForML], tags=["ml"])
async def read_results(
    session: AsyncSession = Depends(get_session)
):
    results_with_features_df = await get_ml_data(session, N_HISTORICAL_ROWS_FOR_PREDICION + 1, for_prediction=True)
    return results_with_features_df.to_dict(orient='records')
