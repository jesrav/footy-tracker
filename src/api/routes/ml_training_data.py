from typing import List

from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.ml_training_data import get_ml_training_data
from models.ml_training_data import MLTrainingData
from core.deps import get_session

router = APIRouter()


@router.get("/ml_training_data/", response_model=MLTrainingData, tags=["stats"])
async def read_results(
        session: AsyncSession = Depends(get_session)
):
    results = await get_ml_training_data(session)
    return results
