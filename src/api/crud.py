from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlalchemy.orm import Session

import models
import schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_nickname(db: Session, nickname: str):
    return db.query(models.User).filter(models.User.nickname == nickname).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        nickname=user.nickname, email=user.email, hash_password=crypto.hash(user.password, rounds=172_434)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(db: Session, email: str, password: str):
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


def get_team(db: Session, team: schemas.TeamBase):
    return (
        db.query(models.Team)
        .filter(
            (models.Team.defender_user_id == team.defender_user_id)
            and (models.Team.attacker_user_id == team.attacker_user_id)
        )
        .first()
    )


def create_team(db: Session, team: schemas.TeamBase):
    db_team = models.Team(
        defender_user_id=team.defender_user_id,
        attacker_user_id=team.attacker_user_id,
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def create_result(db: Session, result: schemas.ResultBase):
    team1_db = get_team(db, team=result.team1)
    if not team1_db:
        team1_db = create_team(db, team=result.team1)
    team2_db = get_team(db, team=result.team2)
    if not team2_db:
        team2_db = create_team(db, team=result.team2)

    db_match = models.Result(
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


def get_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Result).offset(skip).limit(limit).all()


def get_results_for_review(db: Session, reviewer_id):
    results = db.query(models.Result).filter(models.Result.submitter_id != reviewer_id).all()
    results = [r for r in results if reviewer_id in
               [r.team1.defender_user_id, r.team1.attacker_user_id, r.team2.defender_user_id, r.team2.attacker_user_id]
               ]
    return results


def get_result(db: Session, result_id: int) -> models.Result:
    return db.query(models.Result).filter(models.Result.id == result_id).first()


def approve_result(db: Session, result_approval: schemas.ResultApprovalBase):
    db_result_approval = models.ResultApproval(result_submission_id=result_approval.result_submission_id,reviewer_id=result_approval.reviewer_id,approved=result_approval.approved,)
    db.add(db_result_approval)
    db.commit()
    db.refresh(db_result_approval)
    return db_result_approval
