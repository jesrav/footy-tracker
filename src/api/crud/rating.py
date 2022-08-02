from typing import List

from sqlmodel import Session, select

from services.rating import get_updated_elo_player_ratings
from models import rating as rating_models, result as result_models


def add_rating(session: Session, user_id: int, rating: float):
    user_rating = rating_models.UserRating(
        user_id=user_id,
        rating=rating,
    )
    session.add(user_rating)
    session.commit()
    session.refresh(user_rating)
    return user_rating


def update_ratings(session: Session, result: result_models.ResultSubmission) -> List[rating_models.UserRating]:
    new_ratings = get_updated_elo_player_ratings(
        team1_goals=result.goals_team1,
        team2_goals=result.goals_team2,
        team1=result.team1,
        team2=result.team2,
    )
    ratings = []
    for user_rating in new_ratings:
        user_rating.latest_result_at_update_id = result.id
        ratings.append(add_rating(session, user_id=user_rating.user_id, rating=user_rating.rating))
    return ratings


def get_latest_user_rating(session: Session, user_id: int) -> rating_models.UserRating:
    statement = (
        select(rating_models.UserRating)
        .filter(rating_models.UserRating.user_id == user_id)
        .order_by(rating_models.UserRating.created_dt.desc())
    )
    return session.exec(statement).first()


def get_ratings(session: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[rating_models.UserRating]:
    statement = (
        select(rating_models.UserRating)
        .filter(rating_models.UserRating.user_id == user_id)
        .offset(skip).limit(limit)
    )
    return session.exec(statement).all()
