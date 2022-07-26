from datetime import datetime
from typing import Optional, List

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlalchemy.orm import Session
from sqlalchemy import and_

import models
import schemas


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
    return db_user


def login_user(db: Session, email: str, password: str) -> Optional[models.User]:
    try:
        user = get_user_by_email(db, email)
        if not user:
            return None
        if not crypto.verify(password, user.hash_password):
            return None
        else:
            return user
    finally:
        db.close()


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


def get_results_for_review(db: Session, validator_id: int) -> List[models.ResultSubmission]:
    results = db.query(models.ResultSubmission).filter(and_(
        models.ResultSubmission.approved.is_(None),
        models.ResultSubmission.submitter_id != validator_id
    )).all()
    results = [r for r in results if validator_id in
               [r.team1.defender_user_id, r.team1.attacker_user_id, r.team2.defender_user_id, r.team2.attacker_user_id]
               ]
    return results


def validate_results(db: Session, validator_id: int, result_id: int, approved: bool) -> models.ResultSubmission:
    db_result = db.query(models.ResultSubmission).filter(models.ResultSubmission.id == result_id).first()
    db_result.validator_id = validator_id
    db_result.approved = approved
    db_result.validation_dt = datetime.utcnow()
    db.commit()
    return db_result


def get_result(db: Session, result_id: int) -> Optional[models.ResultSubmission]:
    return db.query(models.ResultSubmission).filter(models.ResultSubmission.id == result_id).first()

#
# def create_result_approval(db: Session, result_approval: schemas.ResultApprovalBase):
#     db_result_approval = models.ResultApproval(
#         result_submission_id=result_approval.result_submission_id,
#         reviewer_id=result_approval.reviewer_id,
#         approved=result_approval.approved,
#     )
#     db.add(db_result_approval)
#     db.commit()
#     db.refresh(db_result_approval)
#     return db_result_approval
#
#
# def get_result_approval_by_match(db: Session, result_submission_id: int):
#     return db.query(models.ResultSubmission).filter(models.ResultApproval.result_submission_id == result_submission_id).all()
