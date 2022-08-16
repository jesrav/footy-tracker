from typing import List

from sqlmodel import Session, select

from services.rating import get_updated_player_ratings
from models import rating as rating_models, result as result_models


from typing import List, Optional

from sqlalchemy import func, and_
from sqlmodel import Session, select

from services.rating import get_updated_player_ratings
from models import rating as rating_models, result as result_models


def add_rating(
        session: Session, user_id: int, rating_defence: float, rating_offence: float, result_id: Optional[int] = None
):
    user_rating = rating_models.UserRating(
        user_id=user_id,
        rating_defence=rating_defence,
        rating_offence=rating_offence,
        latest_result_at_update_id=result_id,
    )
    session.add(user_rating)
    session.commit()
    session.refresh(user_rating)
    return user_rating


def update_ratings(session: Session, result: result_models.ResultSubmission) -> List[rating_models.UserRating]:
    new_user_ratings = get_updated_player_ratings(
        team1_goals=result.goals_team1,
        team2_goals=result.goals_team2,
        team1=result.team1,
        team2=result.team2,
    )
    user_ratings = []
    for user_rating in new_user_ratings:
        user_rating.latest_result_at_update_id = result.id
        user_ratings.append(add_rating(
            session,
            user_id=user_rating.user_id,
            rating_defence=user_rating.rating_defence,
            rating_offence=user_rating.rating_offence,
            result_id=result.id,
        ))
    return user_ratings


def get_latest_user_rating(session: Session, user_id: int) -> rating_models.UserRating:
    statement = (
        select(rating_models.UserRating)
        .filter(rating_models.UserRating.user_id == user_id)
        .order_by(rating_models.UserRating.created_dt.desc())
    )
    return session.exec(statement).first()


def get_user_ratings(
        session: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[rating_models.UserRating]:
    statement = (
        select(rating_models.UserRating)
        .filter(rating_models.UserRating.user_id == user_id)
        .offset(skip).limit(limit)
    )
    return session.exec(statement).all()


def get_latest_ratings(session: Session) -> List[rating_models.UserRating]:
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
    return session.exec(statement).all()
