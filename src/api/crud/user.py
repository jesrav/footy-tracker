from typing import Optional, List

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import user as user_models


async def get_user(session: AsyncSession, user_id: int) -> Optional[user_models.User]:
    statement = select(user_models.User).filter(user_models.User.id == user_id)
    result = await session.execute(statement)
    return result.scalars().first()


async def update_user(session: AsyncSession, user_id: int, user_updates: user_models.UserUpdate) -> user_models.User:
    user = await get_user(session, user_id=user_id)
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
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[user_models.User]:
    statement = select(user_models.User).filter(user_models.User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_nickname(session: AsyncSession, nickname: str) -> Optional[user_models.User]:
    statement = select(user_models.User).filter(user_models.User.nickname == nickname)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[user_models.User]:
    statement = select(user_models.User).offset(skip).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()


async def create_user(session: AsyncSession, user: user_models.UserCreate) -> user_models.User:
    user = user_models.User(
        nickname=user.nickname,
        email=user.email,
        motto=user.motto,
        hash_password=crypto.hash(user.password, rounds=172_434),
        profile_pic_path=user.profile_pic_path,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def login_user(session: AsyncSession, email: str, password: str) -> Optional[user_models.User]:
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not crypto.verify(password, user.hash_password):
        return None
    else:
        return user
