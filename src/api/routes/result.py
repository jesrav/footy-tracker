from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

from crud import rating as ratings_crud
from crud import result as result_crud
from crud import user as user_crud
from crud import ranking as ranking_crud
from crud.user_stats import update_user_participant_stats_based_on_result
from models import result as result_models
from database import get_session

router = APIRouter()


@router.get("/users/{user_id}/results_for_approval_by_user/", response_model=List[result_models.ResultSubmissionRead])
async def read_results_for_approval(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await user_crud.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    result = await result_crud.get_results_for_approval_by_user(session, user_id=user.id)
    return result


@router.get("/users/{user_id}/results_for_approval_submitted_by_users_team/", response_model=List[result_models.ResultSubmissionRead])
async def read_results_for_approval(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await user_crud.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await result_crud.get_results_for_approval_submitted_by_users_team(session, user_id=user.id)


@router.post("/users/{user_id}/validate_result/{result_id}/", response_model=result_models.ResultSubmissionRead)
async def validate_result(user_id: int, result_id: int, approved: bool, session: AsyncSession = Depends(get_session)):
    user = await user_crud.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await result_crud.get_result(session, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result submission not found")
    if result.approved is not None:
        raise HTTPException(status_code=404, detail="Result submission already approved or rejected.")
    if result.submitter_id == user_id:
        raise HTTPException(status_code=400, detail="User can not validate result that they submitted themselves")

    # Validator must not be on one of the teams and must not be the same team as the submitter
    if user_id in [result.team1.defender_user_id, result.team1.attacker_user_id]:
        validator_team = result.team1
    elif user_id in [result.team2.defender_user_id, result.team2.attacker_user_id]:
        validator_team = result.team2
    else:
        validator_team = None
    if not validator_team:
        raise HTTPException(status_code=400, detail="Validating user must be part of one of the teams int the match")
    if result.submitter_id in [validator_team.defender_user_id, validator_team.attacker_user_id]:
        raise HTTPException(
            status_code=400, detail="Validating user can not be on the same team as the user that submitted the result"
        )

    validated_result = await result_crud.approve_result(session, validator_id=user.id, result_id=result_id, approved=approved)

    if approved:
        _ = await ratings_crud.update_ratings_from_result(session, result=validated_result)
        _ = await ranking_crud.update_user_rankings(session)
        _ = await update_user_participant_stats_based_on_result(session, result=validated_result)
    return validated_result


@router.post("/results/", response_model=result_models.ResultSubmissionRead)
async def create_result(result: result_models.ResultSubmissionCreate, session: AsyncSession = Depends(get_session)):
    return await result_crud.create_result(session=session, result=result)


@router.get("/results/", response_model=List[result_models.ResultSubmissionRead])
async def read_results(
        for_approval: bool = False,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        session: AsyncSession = Depends(get_session)
):
    results = await result_crud.get_results(session, skip=skip, limit=limit, for_approval=for_approval, user_id=user_id)
    return results


@router.get("/results/{result_id}", response_model=result_models.ResultSubmissionRead)
async def read_result(result_id: int, session: AsyncSession = Depends(get_session)):
    result = await  result_crud.get_result(session, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User result found")
    return result
