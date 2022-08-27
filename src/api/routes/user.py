import os
from typing import List
from pathlib import Path

from fastapi import Depends, HTTPException, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from azure.storage.blob.aio import BlobServiceClient

from crud import user as user_crud
from crud import ranking as ranking_crud
from crud import rating as rating_crud
from crud import user_stats as user_stats_crud
from models import user as user_models
from database import get_session
from services.rating import INITIAL_USER_RATING

router = APIRouter()


@router.post("/users/", response_model=user_models.UserRead)
def create_user(user: user_models.UserCreate, session: Session = Depends(get_session)):
    preexisting_user = user_crud.get_user_by_email(session, email=user.email)
    if preexisting_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = user_crud.create_user(session=session, user=user)
    _ = user_stats_crud.create_first_empty_user_stats(session=session, user_id=user.id)
    _ = rating_crud.add_rating(
        session=session,
        user_id=user.id,
        rating_defence=INITIAL_USER_RATING,
        rating_offence=INITIAL_USER_RATING,
    )
    _ = ranking_crud.update_user_rankings(session=session)
    return user


@router.post("/users/login/", response_model=user_models.UserRead)
def login_user(user: user_models.UserLogin, session: Session = Depends(get_session)):
    user = user_crud.login_user(session, email=user.email, password=user.password)
    if not user:
        raise HTTPException(status_code=404, detail="Email or password not correct")
    return user


@router.get("/users/", response_model=List[user_models.UserRead])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    users = user_crud.get_users(session, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=user_models.UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    users = user_crud.get_user(session, user_id=user_id)
    if users is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users


@router.post("/users/{user_id}/update/", response_model=user_models.UserRead)
def update_user(user_id: int, user_updates: user_models.UserUpdate, session: Session = Depends(get_session)):
    user = user_crud.update_user(session, user_id=user_id, user_updates=user_updates)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email {user_updates.email} does not exist.")
    return user


@router.get("/users/by_email/{email}", response_model=user_models.UserRead)
def read_users_by_email(email: str, session: Session = Depends(get_session)):
    user = user_crud.get_user_by_email(session, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/by_nickname/{nickname}", response_model=user_models.UserRead)
def read_users_by_nickname(nickname: str, session: Session = Depends(get_session)):
    user = user_crud.get_user_by_nickname(session, nickname=nickname)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
