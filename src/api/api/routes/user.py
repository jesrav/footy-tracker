from typing import List

from fastapi import Depends, HTTPException, APIRouter

from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud import user as user_crud
from api.models import user as user_models
from api.core.deps import get_session, get_current_user

router = APIRouter()


@router.get("/users/me", response_model=user_models.UserRead, tags=["users"])
async def get_me(current_user: user_models.User = Depends(get_current_user)):
    return current_user


@router.put("/users/me", response_model=user_models.UserRead, tags=["users"])
async def update_me(
    user_updates: user_models.UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: user_models.User = Depends(get_current_user),
):
    return await user_crud.update_user(session, user_id=current_user.id, user_updates=user_updates)


@router.get("/users/", response_model=List[user_models.UserReadUnauthorized], tags=["users"])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    return await user_crud.get_users(session, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=user_models.UserReadUnauthorized, tags=["users"])
async def read_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    users = await user_crud.get_user(session, user_id=user_id)
    if users is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users
