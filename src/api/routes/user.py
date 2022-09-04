from typing import List

from fastapi import Depends, HTTPException, APIRouter

from sqlmodel.ext.asyncio.session import AsyncSession

from core import deps
from crud import user as user_crud
from models import user as user_models
from core.deps import get_session

router = APIRouter()


@router.get("/users/me", response_model=user_models.UserRead, tags=["users"])
def read_users_me(current_user: user_models.User = Depends(deps.get_current_user)):
    """
    Fetch the current logged in user.
    """

    user = current_user
    return user


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


@router.post("/users/update/", response_model=user_models.UserRead, tags=["users"])
async def update_user(
    user_updates: user_models.UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: user_models.User = Depends(deps.get_current_user),
):
    return await user_crud.update_user(session, user_id=current_user.id, user_updates=user_updates)


# @router.get("/users/by_email/{email}", response_model=user_models.UserRead)
# async def read_users_by_email(
#     email: str,
#     session: AsyncSession = Depends(get_session),
#     current_user: user_models.User = Depends(deps.get_current_user),
# ):
#     user = await user_crud.get_user_by_email(session, email=email)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
#
#
# @router.get("/users/by_nickname/{nickname}", response_model=user_models.UserRead)
# async def read_users_by_nickname(
#     nickname: str,
#     session: AsyncSession = Depends(get_session),
#     current_user: user_models.User = Depends(deps.get_current_user),
# ):
#     user = await user_crud.get_user_by_nickname(session, nickname=nickname)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
