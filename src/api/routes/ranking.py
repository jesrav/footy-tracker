from typing import List

from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.ranking import get_user_rankings
from models.ranking import UserRankingRead
from database import get_session


router = APIRouter()


@router.get("/rankings/", response_model=List[UserRankingRead])
async def read_user_rankings(session: AsyncSession = Depends(get_session)):
    return await get_user_rankings(session)
