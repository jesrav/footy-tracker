from typing import Optional

from sqlmodel import Session, select

from models import team as team_models


def get_team(session: Session, team: team_models.TeamCreate) -> Optional[team_models.Team]:
    statement = (
        select(team_models.Team)
        .filter(
            (team_models.Team.defender_user_id == team.defender_user_id),
            (team_models.Team.attacker_user_id == team.attacker_user_id)
        )
    )
    return session.exec(statement).first()


def create_team(session: Session, team: team_models.TeamCreate) -> team_models.Team:
    db_team = team_models.Team(
        defender_user_id=team.defender_user_id,
        attacker_user_id=team.attacker_user_id,
    )
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team