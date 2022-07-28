from datetime import datetime
from typing import Optional, List

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlalchemy.orm import Session
from sqlalchemy import and_

import models
import schemas


INITIAL_USER_RATING = 1500


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_nickname(db: Session, nickname: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.nickname == nickname).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> Optional[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        nickname=user.nickname, email=user.email, hash_password=crypto.hash(user.password, rounds=172_434)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    add_rating(db, db_user.id, rating=INITIAL_USER_RATING)
    return db_user


def add_rating(db: Session, user_id: int, rating: float):
    user_rating = models.UserRating(
        user_id=user_id,
        rating=rating,
    )
    db.add(user_rating)
    db.commit()
    db.refresh(user_rating)
    return user_rating


def login_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not crypto.verify(password, user.hash_password):
        return None
    else:
        return user


def get_team(db: Session, team: schemas.TeamCreate) -> Optional[models.Team]:
    return (
        db.query(models.Team)
        .filter(
            (models.Team.defender_user_id == team.defender_user_id)
            and (models.Team.attacker_user_id == team.attacker_user_id)
        )
        .first()
    )


def create_team(db: Session, team: schemas.TeamCreate) -> models.Team:
    db_team = models.Team(
        defender_user_id=team.defender_user_id,
        attacker_user_id=team.attacker_user_id,
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def create_result(db: Session, result: schemas.ResultSubmissionCreate) -> models.ResultSubmission:
    team1_db = get_team(db, team=result.team1)
    if not team1_db:
        team1_db = create_team(db, team=result.team1)
    team2_db = get_team(db, team=result.team2)
    if not team2_db:
        team2_db = create_team(db, team=result.team2)

    db_match = models.ResultSubmission(
        submitter_id=result.submitter_id,
        team1_id=team1_db.id,
        team2_id=team2_db.id,
        goals_team1=result.goals_team1,
        goals_team2=result.goals_team2,
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


def get_results(db: Session, skip: int = 0, limit: int = 100) -> List[models.ResultSubmission]:
    return db.query(models.ResultSubmission).offset(skip).limit(limit).all()


def get_results_for_validation(db: Session, validator_id: int) -> List[models.ResultSubmission]:
    """Get results for validation for user

    A user will only get results where they participated, that were not submitted by a teammate.

    :param db: Database session.
    :param validator_id: User id of validator (reviewer).
    :return: A list of result submissions.
    """
    results = db.query(models.ResultSubmission).filter(and_(
        models.ResultSubmission.approved.is_(None),
        models.ResultSubmission.submitter_id != validator_id
    )).all()
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


def validate_result(db: Session, validator_id: int, result_id: int, approved: bool) -> models.ResultSubmission:
    db_result = db.query(models.ResultSubmission).filter(models.ResultSubmission.id == result_id).first()
    db_result.validator_id = validator_id
    db_result.approved = approved
    db_result.validation_dt = datetime.utcnow()
    db.commit()
    return db_result


def get_result(db: Session, result_id: int) -> Optional[models.ResultSubmission]:
    return db.query(models.ResultSubmission).filter(models.ResultSubmission.id == result_id).first()


def simple_elo(
        team1: schemas.TeamOut, team2: schemas.TeamOut, team1_goals: int, team2_goals: int
) -> List[schemas.UserRatingCreate]:
    if team1_goals > team2_goals:
        return [
            team1.defender.latest_rating.get_new_rating(1),
            team1.attacker.latest_rating.get_new_rating(1),
            team2.defender.latest_rating.get_new_rating(-1),
            team2.attacker.latest_rating.get_new_rating(-1),
        ]
    elif team1_goals < team2_goals:
        return [
            team1.defender.latest_rating.get_new_rating(-1),
            team1.attacker.latest_rating.get_new_rating(-1),
            team2.defender.latest_rating.get_new_rating(1),
            team2.attacker.latest_rating.get_new_rating(1),
        ]
    else:
        return [
            team1.defender.latest_rating.get_new_rating(0),
            team1.attacker.latest_rating.get_new_rating(0),
            team2.defender.latest_rating.get_new_rating(0),
            team2.attacker.latest_rating.get_new_rating(0),
        ]


def _add_rating(db: Session, user_rating: schemas.UserRatingCreate) -> models.UserRating:
    db_user_rating = models.UserRating(
        user_id=user_rating.user_id,
        rating=user_rating.rating,
        latest_result_at_update_id=user_rating.latest_result_at_update_id,
    )
    db.add(db_user_rating)
    db.commit()
    db.refresh(db_user_rating)
    return db_user_rating


def update_ratings(db: Session, result: schemas.ResultSubmissionOut) -> List[models.UserRating]:
    new_ratings = simple_elo(
        team1_goals=result.goals_team1,
        team2_goals=result.goals_team2,
        team1=result.team1,
        team2=result.team2,
    )
    db_ratings = []
    for user_rating in new_ratings:
        user_rating.latest_result_at_update_id = result.id
        db_ratings.append(_add_rating(db, user_rating=user_rating))
    return db_ratings
