from typing import List

from fastapi import Depends, HTTPException, APIRouter

from sqlmodel.ext.asyncio.session import AsyncSession

from core import deps
from crud import user as user_crud
from models import user as user_models
from core.deps import get_session

router = APIRouter()


@router.get("/me", response_model=user_models.UserRead, tags=["users"])
async def get_me(current_user: user_models.User = Depends(deps.get_current_user)):
    user = current_user
    return user


@router.post("/me/update/", response_model=user_models.UserRead, tags=["users"])
async def update_me(
    user_updates: user_models.UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: user_models.User = Depends(deps.get_current_user),
):
    return await user_crud.update_user(session, user_id=current_user.id, user_updates=user_updates)


@router.get("/users/", response_model=List[user_models.UserReadUnauthorized], tags=["users"])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    users = await user_crud.get_users(session, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=user_models.UserReadUnauthorized, tags=["users"])
async def read_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    users = await user_crud.get_user(session, user_id=user_id)
    if users is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users
