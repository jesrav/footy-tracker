from typing import List

from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.user_stats import get_user_stats
from models.user_stats import UserStatsRead
from core.deps import get_session

router = APIRouter()


@router.get("/user_stats/", response_model=List[UserStatsRead])
async def read_user_stats(session: AsyncSession = Depends(get_session)):
    return await get_user_stats(session)
