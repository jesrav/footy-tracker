from typing import Optional, List

from passlib.handlers.sha2_crypt import sha512_crypt as crypto

from data import db_session
from data.user import User


def create_account(nickname: str, email: str, password: str) -> User:
    session = db_session.create_session()

    try:
        user = User()
        user.nickname = nickname
        user.email = email
        user.hash_password = crypto.hash(password, rounds=172_434)

        session.add(user)
        session.commit()

        return user
    finally:
        session.close()


def login_user(email: str, password: str) -> Optional[User]:
    session = db_session.create_session()

    try:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            return user

        if not crypto.verify(password, user.hash_password):
            return None

        return user
    finally:
        session.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    session = db_session.create_session()

    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()


def get_user_by_email(email: str) -> Optional[User]:
    session = db_session.create_session()

    try:
        return session.query(User).filter(User.email == email).first()
    finally:
        session.close()


def get_user_by_nickname(nickname: str) -> Optional[User]:
    session = db_session.create_session()

    try:
        return session.query(User).filter(User.nickname == nickname).first()
    finally:
        session.close()


def get_all_users() -> List[User]:
    session = db_session.create_session()
    try:
        return session.query(User).all()
    finally:
        session.close()