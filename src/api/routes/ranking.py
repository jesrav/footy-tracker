from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from crud.ranking import get_user_rankings
from models.ranking import UserRanking
from database import get_session


router = APIRouter()


@router.get("/rankings", response_model=List[UserRanking])
def read_user_rankings(session: Session = Depends(get_session)):
    return get_user_rankings(session)
