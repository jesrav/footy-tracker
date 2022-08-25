from typing import Optional, List

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlmodel import Session, select

from models import user as user_models


def get_user(session: Session, user_id: int) -> Optional[user_models.User]:
    statement = select(user_models.User).filter(user_models.User.id == user_id)
    return session.exec(statement).first()


def update_user(session: Session, user_id: int, user_updates: user_models.UserUpdate) -> user_models.User:
    user = get_user(session, user_id=user_id)
    if not user:
        return user
    if user_updates.email:
        user.email = user_updates.email
    if user_updates.nickname:
        user.nickname = user_updates.nickname
    if user_updates.motto:
        user.motto = user_updates.motto
    if user_updates.profile_pic_path:
        user.profile_pic_path = user_updates.profile_pic_path
    session.commit()
    session.refresh(user)
    return user


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
    user = user_models.User(
        nickname=user.nickname,
        email=user.email,
        motto=user.motto,
        hash_password=crypto.hash(user.password, rounds=172_434),
        profile_pic_path=user.profile_pic_path,
    )
    session.add(user)
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