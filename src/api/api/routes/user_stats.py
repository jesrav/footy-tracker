from typing import List

from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud.user_stats import get_user_stats
from api.models.user_stats import UserStatsRead
from api.core.deps import get_session

router = APIRouter()


@router.get("/user_stats/", response_model=List[UserStatsRead], tags=["stats"])
async def read_user_stats(
    session: AsyncSession = Depends(get_session),
):
    return await get_user_stats(session)
