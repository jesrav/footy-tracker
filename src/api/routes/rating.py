from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from crud import rating as crud_rating
from crud import user as crud_user
from models import rating as rating_models
from core.deps import get_session

router = APIRouter()


@router.get("/ratings/{user_id}/", response_model=List[rating_models.UserRatingRead], tags=["stats"])
async def read_user_rating(user_id: int, skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    user = await crud_user.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud_rating.get_user_ratings(session, user_id=user_id, skip=skip, limit=limit)


@router.get("/ratings/latest", response_model=List[rating_models.UserRatingRead], tags=["stats"])
async def read_latest_ratings(session: AsyncSession = Depends(get_session)):
    return await crud_rating.get_latest_ratings(session)


@router.get("/ratings/latest/{user_id}", response_model=rating_models.UserRatingRead, tags=["stats"])
async def read_latest_user_rating(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await crud_user.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud_rating.get_latest_user_rating(session, user_id=user_id)
