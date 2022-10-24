from typing import List, Optional

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models.result import ResultSubmission
from api.models.user_stats import UserStats


async def get_user_stats(session: AsyncSession) -> List[UserStats]:
    statement = select(UserStats)
    result = await session.execute(statement)
    return result.scalars().all()


async def create_first_empty_user_stats(session: AsyncSession, user_id: int, commit_changes: bool = True):
    statement = select(UserStats).filter(UserStats.user_id == user_id)
    result = await session.execute(statement)
    user_stats = result.scalars().first()
    if user_stats:
        raise ValueError("Can't create first empty users stats, as a stats entry is already present.")
    user_stats = UserStats(user_id=user_id)
    session.add(user_stats)
    if commit_changes:
        await session.commit()
        await session.refresh(user_stats)
    return user_stats


async def update_user_stats(
        session: AsyncSession, user_id: int, result: Optional[ResultSubmission], commit_changes: bool = True
) -> UserStats:
    statement = select(UserStats).filter(UserStats.user_id == user_id)
    db_result = await session.execute(statement)
    user_stats = db_result.scalars().first()

    if user_id in result.team1:
        user_stats.eggs_given += 1 * (result.goals_team2 == 0)
        user_stats.eggs_received += 1 * (result.goals_team1 == 0)
        user_won = (result.goals_team1 > result.goals_team2)
        user_is_defender = user_id == result.team1.defender_user_id
    else:
        user_stats.eggs_given += 1 * (result.goals_team1 == 0)
        user_stats.eggs_received += 1 * (result.goals_team2 == 0)
        user_won = (result.goals_team2 > result.goals_team1)
        user_is_defender = user_id == result.team2.defender_user_id

    if user_is_defender:
        user_stats.games_played_defence += 1
        user_stats.games_won_defence += user_won * 1
    else:
        user_stats.games_played_offence += 1
        user_stats.games_won_offence += user_won * 1

    session.add(user_stats)
    if commit_changes:
        await session.commit()
    return user_stats


async def update_user_participant_stats_based_on_result(
        session: AsyncSession, result: ResultSubmission, commit_changes: bool = True
) -> List[UserStats]:
    updated_user_stats = []
    for user_id in result.match_participants:
        updated_user_stats.append(
            await update_user_stats(session=session, result=result, user_id=user_id, commit_changes=commit_changes)
        )
    return updated_user_stats
