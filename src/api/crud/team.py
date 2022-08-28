from typing import Optional

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import team as team_models


async def get_team(session: AsyncSession, team: team_models.TeamCreate) -> Optional[team_models.Team]:
    statement = (
        select(team_models.Team)
        .filter(
            (team_models.Team.defender_user_id == team.defender_user_id),
            (team_models.Team.attacker_user_id == team.attacker_user_id)
        )
    )
    db_result = await session.execute(statement)
    return db_result.scalars().first()


async def create_team(session: AsyncSession, team: team_models.TeamCreate) -> team_models.Team:
    db_team = team_models.Team(
        defender_user_id=team.defender_user_id,
        attacker_user_id=team.attacker_user_id,
    )
    session.add(db_team)
    await session.commit()
    await session.refresh(db_team)
    return db_team
