from typing import List
from datetime import datetime

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.ranking import UserRanking
from services.ranking import get_updated_user_rankings
from crud.rating import get_latest_ratings


async def get_user_rankings(session: AsyncSession) -> List[UserRanking]:
    statement = select(UserRanking)
    result = await session.execute(statement)
    return result.scalars().all()


async def update_user_rankings(session: AsyncSession) -> List[UserRanking]:
    statement = select(UserRanking)
    result = await session.execute(statement)
    current_rankings = result.scalars().all()
    latest_user_ratings = await get_latest_ratings(session=session)

    updated_user_rankings = await get_updated_user_rankings(latest_user_ratings)

    updated_or_new_user_rankings_dict = {r.user_id: r for r in current_rankings}
    for ranking in updated_user_rankings:
        if ranking.user_id in updated_or_new_user_rankings_dict:
            updated_or_new_user_rankings_dict[ranking.user_id].defensive_ranking = ranking.defensive_ranking
            updated_or_new_user_rankings_dict[ranking.user_id].offensive_ranking = ranking.offensive_ranking
            updated_or_new_user_rankings_dict[ranking.user_id].overall_ranking = ranking.overall_ranking
            updated_or_new_user_rankings_dict[ranking.user_id].updated_dt = datetime.utcnow()
        else:
            updated_or_new_user_rankings_dict[ranking.user_id] = ranking
    updated_or_new_user_rankings = list(updated_or_new_user_rankings_dict.values())

    for user_ranking in updated_or_new_user_rankings:
        session.add(user_ranking)
    await session.commit()
    for user_ranking in updated_or_new_user_rankings:
        await session.refresh(user_ranking)
    return updated_or_new_user_rankings
