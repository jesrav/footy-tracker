from sqlalchemy.orm import selectinload
from sqlmodel import select

from typing import List, Optional

from sqlalchemy import func, and_
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.models import rating as rating_models, result as result_models
from api.services.rating import update_ratings


async def add_rating(
    session: AsyncSession,
    user_id: int,
    rating_defence: float,
    rating_offence: float,
    result_id: Optional[int] = None,
    commit_changes: bool = True
):
    user_rating = rating_models.UserRating(
        user_id=user_id,
        rating_defence=rating_defence,
        rating_offence=rating_offence,
        overall_rating=(rating_defence + rating_offence) / 2,
        latest_result_at_update_id=result_id,
    )
    session.add(user_rating)
    if commit_changes:
        await session.commit()
    return user_rating


async def update_ratings_from_result(
        session: AsyncSession, result: result_models.ResultSubmission, commit_changes: bool = True
) -> List[rating_models.UserRating]:
    new_user_ratings = await get_updated_player_ratings(
        session=session,
        team1_goals=result.goals_team1,
        team2_goals=result.goals_team2,
        team1_defender_id=result.team1.defender_user_id,
        team1_attacker_id=result.team1.attacker_user_id,
        team2_defender_id=result.team2.defender_user_id,
        team2_attacker_id=result.team2.attacker_user_id,
    )
    user_ratings = []
    for user_rating in new_user_ratings:
        user_rating.latest_result_at_update_id = result.id
        user_ratings.append(await add_rating(
            session,
            user_id=user_rating.user_id,
            rating_defence=user_rating.rating_defence,
            rating_offence=user_rating.rating_offence,
            result_id=result.id,
            commit_changes=commit_changes,
        ))
    return user_ratings


async def get_latest_user_rating(session: AsyncSession, user_id: int) -> rating_models.UserRating:
    statement = (
        select(rating_models.UserRating)
        .filter(rating_models.UserRating.user_id == user_id)
        .order_by(rating_models.UserRating.created_dt.desc())
    )
    result = await session.execute(statement.options(selectinload(rating_models.UserRating.user)))
    return result.scalars().first()


async def get_user_ratings(
    session: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[rating_models.UserRating]:
    statement = (
        select(rating_models.UserRating)
        .filter(rating_models.UserRating.user_id == user_id)
        .offset(skip).limit(limit)
    )
    result = await session.execute(statement.options(selectinload(rating_models.UserRating.user)))
    return result.scalars().all()


async def get_latest_ratings(session: AsyncSession) -> List[rating_models.UserRating]:
    subquery = (
        select(rating_models.UserRating.user_id, func.max(rating_models.UserRating.created_dt).label('maxdate'))
        .group_by(rating_models.UserRating.user_id)
        .subquery('t2')
    )
    statement = (
        select(rating_models.UserRating)
        .join(
            subquery, and_(rating_models.UserRating.user_id == subquery.c.user_id,
            rating_models.UserRating.created_dt == subquery.c.maxdate)
        )
    )
    result = await session.execute(statement.options(selectinload(rating_models.UserRating.user)))
    return result.scalars().all()


async def get_updated_player_ratings(
    session: AsyncSession,
    team1_defender_id: int,
    team1_attacker_id: int,
    team2_defender_id: int,
    team2_attacker_id: int,
    team1_goals: int,
    team2_goals: int,
) -> List[rating_models.UserRatingCreate]:
    team1_defender_rating = await get_latest_user_rating(session=session, user_id=team1_defender_id)
    team1_attacker_rating = await get_latest_user_rating(session=session, user_id=team1_attacker_id)
    team2_defender_rating = await get_latest_user_rating(session=session, user_id=team2_defender_id)
    team2_attacker_rating = await get_latest_user_rating(session=session, user_id=team2_attacker_id)

    team1_rating = team1_defender_rating.rating_defence + team1_attacker_rating.rating_offence
    team2_rating = team2_defender_rating.rating_defence + team2_attacker_rating.rating_offence

    if team1_goals > team2_goals:
        new_team1_rating, new_team2_rating = await update_ratings(team1_rating, team2_rating, team1_goals, team2_goals)
    elif team1_goals < team2_goals:
        new_team2_rating, new_team1_rating = await update_ratings(team2_rating, team1_rating, team2_goals, team1_goals)
    else:
        raise ValueError("There must be a winner. team1_goals ")

    team1_rating_delta = new_team1_rating - team1_rating
    team2_rating_delta = new_team2_rating - team2_rating

    return [
        await team1_defender_rating.get_new_rating(rating_delta_defence=team1_rating_delta),
        await team1_attacker_rating.get_new_rating(rating_delta_offence=team1_rating_delta),
        await team2_defender_rating.get_new_rating(rating_delta_defence=team2_rating_delta),
        await team2_attacker_rating.get_new_rating(rating_delta_offence=team2_rating_delta),
    ]
