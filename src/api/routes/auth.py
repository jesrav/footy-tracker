from typing import Any, Union

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.auth import authenticate, create_access_token
from crud import user as user_crud, user_stats as user_stats_crud, rating as rating_crud, ranking as ranking_crud
from core.deps import get_session
from core.config import settings
from models import user as user_models


router = APIRouter()


@router.post("/auth/signup/", response_model=user_models.UserRead, status_code=201, tags=["auth"])
async def signup(user: user_models.UserCreate, session: AsyncSession = Depends(get_session)) -> Any:
    preexisting_user = await user_crud.get_user_by_email(session, email=user.email)
    """Sign up user and create first user rating and empty stats."""
    if preexisting_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await user_crud.create_user(session=session, user=user, commit_changes=False)
    _ = await user_stats_crud.create_first_empty_user_stats(session=session, user_id=user.id, commit_changes=False)
    _ = await rating_crud.add_rating(
        session=session,
        user_id=user.id,
        rating_defence=settings.INITIAL_USER_RATING,
        rating_offence=settings.INITIAL_USER_RATING,
        commit_changes=False,
    )
    _ = await ranking_crud.update_user_rankings(session=session, commit_changes=False)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/auth/login", tags=["auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
) -> Any:
    """
    Get the JWT for a user with data from OAuth2 request form body.
    """

    user = await authenticate(session=session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {
        "access_token": create_access_token(user_id=user.id),
        "token_type": "bearer",
    }




