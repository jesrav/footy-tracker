import io

from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import StreamingResponse

from crud.ml_training_data import get_ml_training_data
from core.deps import get_session

router = APIRouter()


@router.get("/ml/data/", response_class=StreamingResponse, tags=["stats"])
async def read_results(
        session: AsyncSession = Depends(get_session)
):
    results_with_features_df = await get_ml_training_data(session)
    stream = io.StringIO()

    results_with_features_df.to_csv(stream, index=False)
    response = StreamingResponse(
        iter([stream.getvalue()]),
         media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return response
