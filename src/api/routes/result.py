from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession

from core import deps
from crud import rating as ratings_crud
from crud import result as result_crud
from crud import ranking as ranking_crud
from crud.user import get_user
from crud.user_stats import update_user_participant_stats_based_on_result
from models import result as result_models
from models import user as user_models
from core.deps import get_session
from services.ml import add_prediction_background_tasks

router = APIRouter()


@router.post("/results/", response_model=result_models.ResultSubmissionRead, tags=["results"])
async def create_result(
    result: result_models.ResultSubmissionCreate,
    ml_prediction_background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_user: user_models.User = Depends(deps.get_current_user),
):
    if current_user.id not in [
        result.team1.defender_user_id,
        result.team1.attacker_user_id,
        result.team2.defender_user_id,
        result.team2.attacker_user_id,
    ]:
        raise HTTPException(
            status_code=400, detail="Submitter must be on one of the teams."
        )
    for user_id in [
        result.team1.defender_user_id,
        result.team1.attacker_user_id,
        result.team1.attacker_user_id,
        result.team2.defender_user_id,
    ]:
        if not await get_user(session=session, user_id=user_id):
            raise HTTPException(
                status_code=400, detail=f"One of the user id's does not exist."
            )
    result = await result_crud.create_result(session=session, submitter=current_user, result=result)

    await add_prediction_background_tasks(
        result=result,
        ml_prediction_background_tasks=ml_prediction_background_tasks,
        session=session,
    )
    return result


@router.get("/results/", response_model=List[result_models.ResultSubmissionRead], tags=["results"])
async def read_results(
        for_approval: bool = False,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        session: AsyncSession = Depends(get_session)
):
    results = await result_crud.get_results(session, skip=skip, limit=limit, for_approval=for_approval, user_id=user_id)
    return results


@router.get("/results/{result_id}", response_model=result_models.ResultSubmissionRead, tags=["results"])
async def read_result(result_id: int, session: AsyncSession = Depends(get_session)):
    result = await result_crud.get_result(session, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/results_for_approval_by_user/", response_model=List[result_models.ResultSubmissionRead], tags=["results"])
async def read_results_for_approval(
    session: AsyncSession = Depends(get_session),
    current_user: user_models.User = Depends(deps.get_current_user),
):
    result = await result_crud.get_results_for_approval_by_user(session, user_id=current_user.id)
    return result


@router.get(
    "/results_for_approval_submitted_by_users_team/",
    response_model=List[result_models.ResultSubmissionRead],
    tags=["results"]
)
async def read_results_for_approval(
    session: AsyncSession = Depends(get_session),
    current_user: user_models.User = Depends(deps.get_current_user),
):
    return await result_crud.get_results_for_approval_submitted_by_users_team(session, user_id=current_user.id)


@router.post("/validate_result/{result_id}/", response_model=result_models.ResultSubmissionRead, tags=["results"])
async def validate_result(
    result_id: int,
    approved: bool,
    session: AsyncSession = Depends(get_session),
    current_user: user_models.User = Depends(deps.get_current_user),
):
    result = await result_crud.get_result(session, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result submission not found")
    if result.approved is not None:
        raise HTTPException(status_code=404, detail="Result submission already approved or rejected.")
    if result.submitter_id == current_user:
        raise HTTPException(status_code=400, detail="User can not validate result that they submitted themselves")

    # Validator must not be on one of the teams and must not be the same team as the submitter
    if current_user.id in [result.team1.defender_user_id, result.team1.attacker_user_id]:
        validator_team = result.team1
    elif current_user.id in [result.team2.defender_user_id, result.team2.attacker_user_id]:
        validator_team = result.team2
    else:
        validator_team = None
    if not validator_team:
        raise HTTPException(status_code=400, detail="Validating user must be part of one of the teams int the match")
    if result.submitter_id in [validator_team.defender_user_id, validator_team.attacker_user_id]:
        raise HTTPException(
            status_code=400, detail="Validating user can not be on the same team as the user that submitted the result"
        )

    validated_result = await result_crud.approve_result(
        session, validator_id=current_user.id, result_id=result_id, approved=approved, commit_changes=False
    )
    if approved:
        _ = await ratings_crud.update_ratings_from_result(session, result=validated_result, commit_changes=False)
        _ = await ranking_crud.update_user_rankings(session, commit_changes=False)
        _ = await update_user_participant_stats_based_on_result(session, result=validated_result, commit_changes=False)

    await session.commit()
    await session.refresh(validated_result)
    refreshed_validated_result = await result_crud.get_result(session, result_id=validated_result.id)
    return refreshed_validated_result
