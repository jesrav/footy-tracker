from typing import List

from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud.ranking import get_user_rankings
from api.models.ranking import UserRankingRead
from api.core.deps import get_session

router = APIRouter()


@router.get("/rankings/", response_model=List[UserRankingRead], tags=["stats"])
async def read_user_rankings(session: AsyncSession = Depends(get_session)):
    return await get_user_rankings(session)
