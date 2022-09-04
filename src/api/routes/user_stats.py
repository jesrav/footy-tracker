from typing import List

from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from core import deps
from crud.user_stats import get_user_stats
from models.user import User
from models.user_stats import UserStatsRead
from core.deps import get_session

router = APIRouter()


@router.get("/user_stats/", response_model=List[UserStatsRead], tags=["stats"])
async def read_user_stats(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
):
    return await get_user_stats(session)
