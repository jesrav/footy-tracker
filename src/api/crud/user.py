from typing import Optional, List

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlmodel import Session, select

from services.rating import INITIAL_USER_RATING
from models import user as user_models, rating as rating_models


def get_user(session: Session, user_id: int) -> Optional[user_models.User]:
    statement = select(user_models.User).filter(user_models.User.id == user_id)
    return session.exec(statement).one()


def get_user_by_email(session: Session, email: str) -> Optional[user_models.User]:
    statement = select(user_models.User).filter(user_models.User.email == email)
    return session.exec(statement).first()


def get_user_by_nickname(session: Session, nickname: str) -> Optional[user_models.User]:
    statement = select(user_models.User).filter(user_models.User.nickname == nickname)
    return session.exec(statement).first()


def get_users(session: Session, skip: int = 0, limit: int = 100) -> List[user_models.User]:
    statement = select(user_models.User).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_user(session: Session, user: user_models.UserCreate) -> user_models.User:
    # Create user
    user = user_models.User(
        nickname=user.nickname, email=user.email, hash_password=crypto.hash(user.password, rounds=172_434)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    # Create initial rating
    user_rating = rating_models.UserRating(
        user_id=user.id,
        rating=INITIAL_USER_RATING,
    )
    session.add(user_rating)
    session.commit()
    session.refresh(user)
    return user


def login_user(session: Session, email: str, password: str) -> Optional[user_models.User]:
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not crypto.verify(password, user.hash_password):
        return None
    else:
        return user