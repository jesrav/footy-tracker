from datetime import datetime
from typing import Optional, List

import elo
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlmodel import Session, select

import schemas

INITIAL_USER_RATING = 1200

# User lager K factor than the default
elo.K_FACTOR = 32


def get_user(session: Session, user_id: int) -> Optional[schemas.User]:
    statement = select(schemas.User).filter(schemas.User.id == user_id)
    return session.exec(statement).one()


def get_user_by_email(session: Session, email: str) -> Optional[schemas.User]:
    statement = select(schemas.User).filter(schemas.User.email == email)
    return session.exec(statement).one()


def get_user_by_nickname(session: Session, nickname: str) -> Optional[schemas.User]:
    statement = select(schemas.User).filter(schemas.User.nickname == nickname)
    return session.exec(statement).one()


def get_users(session: Session, skip: int = 0, limit: int = 100) -> List[schemas.User]:
    statement = select(schemas.User).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_user(session: Session, user: schemas.UserCreate) -> schemas.User:
    # Create user
    user = schemas.User(
        nickname=user.nickname, email=user.email, hash_password=crypto.hash(user.password, rounds=172_434)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    # Create initial rating
    user_rating = schemas.UserRating(
        user_id=user.id,
        rating=INITIAL_USER_RATING,
    )
    session.add(user_rating)
    session.commit()
    session.refresh(user)
    return user


def add_rating(session: Session, user_id: int, rating: float):
    user_rating = schemas.UserRating(
        user_id=user_id,
        rating=rating,
    )
    session.add(user_rating)
    session.commit()
    session.refresh(user_rating)
    return user_rating


def login_user(session: Session, email: str, password: str) -> Optional[schemas.User]:
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not crypto.verify(password, user.hash_password):
        return None
    else:
        return user


def get_team(session: Session, team: schemas.TeamCreate) -> Optional[schemas.Team]:
    statement = (
        select(schemas.Team)
        .filter(
            (schemas.Team.defender_user_id == team.defender_user_id),
            (schemas.Team.attacker_user_id == team.attacker_user_id)
        )
    )
    return session.exec(statement).first()


def create_team(session: Session, team: schemas.TeamCreate) -> schemas.Team:
    db_team = schemas.Team(
        defender_user_id=team.defender_user_id,
        attacker_user_id=team.attacker_user_id,
    )
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


def create_result(session: Session, result: schemas.ResultSubmissionCreate) -> schemas.ResultSubmission:
    team1_db = get_team(session, team=result.team1)
    if not team1_db:
        team1_db = create_team(session, team=result.team1)
    team2_db = get_team(session, team=result.team2)
    if not team2_db:
        team2_db = create_team(session, team=result.team2)

    result = schemas.ResultSubmission(
        submitter_id=result.submitter_id,
        team1_id=team1_db.id,
        team2_id=team2_db.id,
        goals_team1=result.goals_team1,
        goals_team2=result.goals_team2,
    )
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


def get_results(session: Session, skip: int = 0, limit: int = 100) -> List[schemas.ResultSubmission]:
    statement = select(schemas.ResultSubmission).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_results_for_validation(session: Session, validator_id: int) -> List[schemas.ResultSubmission]:
    """Get results for validation for user

    A user will only get results where they participated, that were not submitted by a teammate.

    :param session: Database session.
    :param validator_id: User id of validator (reviewer).
    :return: A list of result submissions.
    """
    statement = select(schemas.ResultSubmission).filter(
        schemas.ResultSubmission.approved == None,
        schemas.ResultSubmission.submitter_id != validator_id
    )
    results = session.exec(statement).all()

    results_with_validator_participation = [
        r for r in results if validator_id in
       [r.team1.defender_user_id, r.team1.attacker_user_id, r.team2.defender_user_id, r.team2.attacker_user_id]
    ]
    validator_teams = [
        r.team1
        if validator_id in [r.team1.defender_user_id, r.team1.attacker_user_id]
        else r.team2
        for r in results_with_validator_participation
    ]
    results_validator_and_submitter_not_teammates = [
        r for i, r in enumerate(results_with_validator_participation)
        if r.submitter_id not in [validator_teams[i].defender_user_id, validator_teams[i].attacker_user_id]
    ]
    return results_validator_and_submitter_not_teammates


def validate_result(session: Session, validator_id: int, result_id: int, approved: bool) -> schemas.ResultSubmission:
    statement = select(schemas.ResultSubmission).filter(schemas.ResultSubmission.id == result_id)
    result = session.exec(statement).one()
    result.validator_id = validator_id
    result.approved = approved
    result.validation_dt = datetime.utcnow()
    session.commit()
    return result


def get_result(session: Session, result_id: int) -> Optional[schemas.ResultSubmission]:
    statement = select(schemas.ResultSubmission).filter(schemas.ResultSubmission.id == result_id)
    return session.exec(statement).one()


def get_updated_elo_player_ratings(
        team1: schemas.Team, team2: schemas.Team, team1_goals: int, team2_goals: int
) -> List[schemas.UserRatingCreate]:
    team1_rating = team1.defender.latest_rating.rating + team1.attacker.latest_rating.rating
    team2_rating = team2.defender.latest_rating.rating + team2.attacker.latest_rating.rating

    if team1_goals > team2_goals:
        new_team1_rating, new_team2_rating = elo.rate_1vs1(team1_rating, team2_rating)
    elif team1_goals < team2_goals:
        new_team2_rating, new_team1_rating = elo.rate_1vs1(team2_rating, team1_rating)
    else:
        new_team1_rating, new_team2_rating = team1_rating, team2_rating

    team1_rating_delta = new_team1_rating - team1_rating
    team2_rating_delta = new_team2_rating - team2_rating

    return [
        team1.defender.latest_rating.get_new_rating(rating_delta=team1_rating_delta),
        team1.attacker.latest_rating.get_new_rating(rating_delta=team1_rating_delta),
        team2.defender.latest_rating.get_new_rating(rating_delta=team2_rating_delta),
        team2.attacker.latest_rating.get_new_rating(rating_delta=team2_rating_delta),
    ]


def _add_rating(db: Session, user_rating: schemas.UserRatingCreate) -> schemas.UserRating:
    db_user_rating = schemas.UserRating(
        user_id=user_rating.user_id,
        rating=user_rating.rating,
        latest_result_at_update_id=user_rating.latest_result_at_update_id,
    )
    db.add(db_user_rating)
    db.commit()
    db.refresh(db_user_rating)
    return db_user_rating


def update_ratings(session: Session, result: schemas.ResultSubmission) -> List[schemas.UserRating]:
    new_ratings = get_updated_elo_player_ratings(
        team1_goals=result.goals_team1,
        team2_goals=result.goals_team2,
        team1=result.team1,
        team2=result.team2,
    )
    db_ratings = []
    for user_rating in new_ratings:
        user_rating.latest_result_at_update_id = result.id
        db_ratings.append(_add_rating(session, user_rating=user_rating))
    return db_ratings


def get_latest_user_rating(session: Session, user_id: int) -> schemas.UserRating:
    statement = (
        select(schemas.UserRating)
        .filter(schemas.UserRating.user_id == user_id)
        .order_by(schemas.UserRating.created_dt.desc())
    )
    return session.exec(statement).first()


def get_ratings(session: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[schemas.UserRating]:
    statement = (
        select(schemas.UserRating)
        .filter(schemas.UserRating.user_id == user_id)
        .offset(skip).limit(limit)
    )
    return session.exec(statement).all()
