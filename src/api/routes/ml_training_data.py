from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from core import deps
from crud import rating as ratings_crud
from crud import result as result_crud
from models import result as result_models
from models import user as user_models
from core.deps import get_session

router = APIRouter()


@router.get("/ml/", response_model=List[result_models.ResultSubmissionRead], tags=["results"])
async def read_results(
        for_approval: bool = False,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        session: AsyncSession = Depends(get_session)
):
    results = await result_crud.get_results(session, skip=skip, limit=limit, for_approval=for_approval, user_id=user_id)
    return results
