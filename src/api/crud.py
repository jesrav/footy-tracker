from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlalchemy.orm import Session

import models, schemas


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


def create_match(db: Session, match: schemas.MatchBase):
    team1_db = get_team(db, team=match.team1)
    if not team1_db:
        team1_db = create_team(db, team=match.team1)
    team2_db = get_team(db, team=match.team2)
    if not team2_db:
        team2_db = create_team(db, team=match.team2)

    db_match = models.ResultSubmission(
        team1_id=team1_db.id,
        team2_id=team2_db.id,
        goals_team1=match.goals_team1,
        goals_team2=match.goals_team2,
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match
