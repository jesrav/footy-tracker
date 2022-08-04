from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from crud import rating as crud_rating
from crud import user as crud_user
from models import rating as rating_models
from database import get_session


router = APIRouter()


@router.get("/ratings/{user_id}", response_model=List[rating_models.UserRatingRead])
def read_ratings(user_id: int, skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    user = crud_user.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_rating.get_ratings(session, user_id=user_id, skip=skip, limit=limit)


@router.get("/ratings/{user_id}/latest", response_model=rating_models.UserRatingRead)
def read_latest_rating(user_id: int, session: Session = Depends(get_session)):
    user = crud_user.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_rating.get_latest_user_rating(session, user_id=user_id)
