from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from crud.user_stats import get_user_stats
from models.user_stats import UserStatsRead
from database import get_session


router = APIRouter()


@router.get("/user_stats/", response_model=List[UserStatsRead])
def read_user_stats(session: Session = Depends(get_session)):
    return get_user_stats(session)
