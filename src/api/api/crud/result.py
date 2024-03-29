from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud.team import get_team, create_team
from api.models import result as result_models
from api.models import user as user_models


async def create_result(
    session: AsyncSession,
    submitter: user_models.User,
    result: result_models.ResultSubmissionCreate
) -> result_models.ResultSubmission:
    team1_db = await get_team(session, team=result.team1)
    if not team1_db:
        team1_db = await create_team(session, team=result.team1)
    team2_db = await get_team(session, team=result.team2)
    if not team2_db:
        team2_db = await create_team(session, team=result.team2)

    result = result_models.ResultSubmission(
        submitter_id=submitter.id,
        team1_id=team1_db.id,
        team2_id=team2_db.id,
        goals_team1=result.goals_team1,
        goals_team2=result.goals_team2,
    )
    session.add(result)
    await session.commit()
    refreshed_result = await get_result(session=session, result_id=result.id)
    return refreshed_result


async def get_results(
    session: AsyncSession, skip: int = 0, limit: int = 100, for_approval: bool = False, user_id: Optional[int] = None
) -> List[result_models.ResultSubmission]:
    statement = (
        select(result_models.ResultSubmission)
        .order_by(result_models.ResultSubmission.created_dt.desc())
        .offset(skip).limit(limit)
    )
    if for_approval:
        statement = statement.filter(result_models.ResultSubmission.approved == None)
    else:
        statement = statement.filter(result_models.ResultSubmission.approved != None)

    db_result = await session.execute(statement.options(
        joinedload('validator'),
        joinedload('submitter'),
        joinedload('team1'),
        joinedload('team2'),
        joinedload('team1.defender'),
        joinedload('team1.attacker'),
        joinedload('team2.defender'),
        joinedload('team2.attacker'),
    ))
    if not user_id:
        results = db_result.scalars().all()
    else:
        all_results = db_result.scalars().all()
        results = [r for r in all_results if user_id in r.match_participants]
    return results


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
            results_with_user_participation.append(r)
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
    db_result = await session.execute(statement.options(
        joinedload('validator'),
        joinedload('submitter'),
        joinedload('team1'),
        joinedload('team2'),
        joinedload('team1.defender'),
        joinedload('team1.attacker'),
        joinedload('team2.defender'),
        joinedload('team2.attacker'),
    ))

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
    db_result = await session.execute(statement.options(
        joinedload('validator'),
        joinedload('submitter'),
        joinedload('team1'),
        joinedload('team2'),
        joinedload('team1.defender'),
        joinedload('team1.attacker'),
        joinedload('team2.defender'),
        joinedload('team2.attacker'),
    ))
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
        session: AsyncSession, validator_id: int, result_id: int, approved: bool, commit_changes: bool = True
) -> result_models.ResultSubmission:
    statement = select(result_models.ResultSubmission).filter(result_models.ResultSubmission.id == result_id)
    db_result = await session.execute(statement.options(
        joinedload('validator'),
        joinedload('submitter'),
        joinedload('team1'),
        joinedload('team2'),
        joinedload('team1.defender'),
        joinedload('team1.attacker'),
        joinedload('team2.defender'),
        joinedload('team2.attacker'),
    ))
    result = db_result.scalars().one()
    result.validator_id = validator_id
    result.approved = approved
    result.validation_dt = datetime.utcnow()
    if commit_changes:
        await session.commit()
    return result


async def get_result(session: AsyncSession, result_id: int) -> Optional[result_models.ResultSubmission]:
    statement = select(result_models.ResultSubmission).filter(result_models.ResultSubmission.id == result_id)
    db_result = await session.execute(statement.options(
        joinedload('validator'),
        joinedload('submitter'),
        joinedload('team1'),
        joinedload('team2'),
        joinedload('team1.defender'),
        joinedload('team1.attacker'),
        joinedload('team2.defender'),
        joinedload('team2.attacker'),
    ))
    return db_result.scalars().first()


async def get_latest_approved_result(session: AsyncSession) -> List[result_models.ResultSubmission]:

    statement = (
        select(result_models.ResultSubmission)
        .filter(result_models.ResultSubmission.approved != None)
        .order_by(result_models.ResultSubmission.id.desc())
    )

    db_result = await session.execute(statement)
    return db_result.scalars().first()
