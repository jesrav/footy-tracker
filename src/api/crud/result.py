from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.team import get_team, create_team
from models import result as result_models


async def create_result(session: AsyncSession, result: result_models.ResultSubmissionCreate) -> result_models.ResultSubmission:
    team1_db = get_team(session, team=result.team1)
    if not team1_db:
        team1_db = create_team(session, team=result.team1)
    team2_db = get_team(session, team=result.team2)
    if not team2_db:
        team2_db = create_team(session, team=result.team2)

    result = result_models.ResultSubmission(
        submitter_id=result.submitter_id,
        team1_id=team1_db.id,
        team2_id=team2_db.id,
        goals_team1=result.goals_team1,
        goals_team2=result.goals_team2,
    )
    session.add(result)
    await session.commit()
    await session.refresh(result)
    return result


async def get_results(
        session: AsyncSession, skip: int = 0, limit: int = 100, for_approval: bool = False, user_id: Optional[int] = None
) -> List[result_models.ResultSubmission]:
    statement = select(result_models.ResultSubmission).offset(skip).limit(limit)

    if for_approval:
        statement = statement.filter(result_models.ResultSubmission.approved == None)
    else:
        statement = statement.filter(result_models.ResultSubmission.approved != None)

    db_result = await session.execute(statement)
    if not user_id:
        return db_result.scalars().all()
    else:
        all_results = db_result.scalars().all()
        return [r for r in all_results if user_id in r.match_participants]


async def _get_results_with_user_participation(
        results: List[result_models.ResultSubmission],
        user_id: int,
) -> List[result_models.ResultSubmission]:
    results_with_user_participation = []
    for r in results:
        if user_id in [
            r.team1.defender_user_id,
            r.team1.attacker_user_id,
            r.team2.defender_user_id,
            r.team2.attacker_user_id
        ]:
            results_with_user_participation.append()
    return results_with_user_participation


async def get_results_for_approval_by_user(session: AsyncSession, user_id: int) -> List[result_models.ResultSubmission]:
    """Get results for approval by user

    A user will only get results where they participated, that were not submitted by a teammate.

    :param session: Database session
    :param user_id: User id of validator (reviewer)
    :return: A list of result submissions.
    """

    statement = select(result_models.ResultSubmission).filter(
        result_models.ResultSubmission.approved == None,
        result_models.ResultSubmission.submitter_id != user_id
    )
    db_result = await session.execute(statement)
    results = db_result.scalars().all()

    results_with_user_participation = await _get_results_with_user_participation(results, user_id)

    user_teams = [
        r.team1
        if user_id in [r.team1.defender_user_id, r.team1.attacker_user_id]
        else r.team2
        for r in results_with_user_participation
    ]

    results_user_and_submitter_not_teammates = [
        r for i, r in enumerate(results_with_user_participation)
        if r.submitter_id not in [user_teams[i].defender_user_id, user_teams[i].attacker_user_id]
    ]
    return results_user_and_submitter_not_teammates


async def get_results_for_approval_submitted_by_users_team(session: AsyncSession, user_id: int) -> List[result_models.ResultSubmission]:
    """Get results for approval submitted by the user or the users teammate.

    :param session: Database session
    :param user_id: User id of validator (reviewer)
    :return: A list of result submissions.
    """

    statement = select(result_models.ResultSubmission).filter(
        result_models.ResultSubmission.approved == None,
    )
    db_result = await session.execute(statement)
    results = db_result.scalars().all()

    results_with_user_participation = await _get_results_with_user_participation(results, user_id)

    user_teams = [
        r.team1
        if user_id in [r.team1.defender_user_id, r.team1.attacker_user_id]
        else r.team2
        for r in results_with_user_participation
    ]

    results_submitter_in_users_team = [
        r for i, r in enumerate(results_with_user_participation)
        if r.submitter_id in [user_teams[i].defender_user_id, user_teams[i].attacker_user_id]
    ]
    return results_submitter_in_users_team


async def approve_result(
        session: AsyncSession, validator_id: int, result_id: int, approved: bool
) -> result_models.ResultSubmission:
    statement = select(result_models.ResultSubmission).filter(result_models.ResultSubmission.id == result_id)
    db_result = await session.execute(statement)
    result = db_result.scalars().one()
    result.validator_id = validator_id
    result.approved = approved
    result.validation_dt = datetime.utcnow()
    await session.commit()
    return result


async def get_result(session: AsyncSession, result_id: int) -> Optional[result_models.ResultSubmission]:
    statement = select(result_models.ResultSubmission).filter(result_models.ResultSubmission.id == result_id)
    db_result = await session.execute(statement)
    return db_result.scalars().one()
