from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from crud import user as user_crud
from crud import ranking as ranking_crud
from models import user as user_models
from database import get_session

router = APIRouter()


@router.post("/users/", response_model=user_models.UserRead)
def create_user(user: user_models.UserCreate, session: Session = Depends(get_session)):
    preexisting_user = user_crud.get_user_by_email(session, email=user.email)
    if preexisting_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = user_crud.create_user(session=session, user=user)
    ranking_crud.update_user_rankings(session=session)
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
