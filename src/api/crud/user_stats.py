from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from models.result import ResultSubmission
from models.user_stats import UserStats


def get_user_stats(session: Session) -> List[UserStats]:
    statement = select(UserStats)
    return session.exec(statement).all()


def create_first_empty_user_stats(session: Session, user_id: int):
    statement = select(UserStats).filter(UserStats.user_id == user_id)
    user_stats = session.exec(statement).first()
    if user_stats:
        raise ValueError("Can't create first empty users stats, as a stats entry is already present.")
    user_stats = UserStats(user_id=user_id)
    session.add(user_stats)
    session.commit()
    session.refresh(user_stats)
    return user_stats


def update_user_stats(session: Session, user_id: int, result: Optional[ResultSubmission]) -> UserStats:
    statement = select(UserStats).filter(UserStats.user_id == user_id)
    user_stats = session.exec(statement).first()

    if user_id in result.team1:
        user_stats.eggs_given += 1 * (result.goals_team2 == 0)
        user_stats.eggs_received += 1 * (result.goals_team1 == 0)
        user_won = (result.goals_team1 > result.goals_team2)
        user_is_defender = user_id == result.team1.defender_user_id
    else:
        user_stats.eggs_given += 1 * (result.goals_team1 == 0)
        user_stats.eggs_received += 1 * (result.goals_team2 == 0)
        user_won = (result.goals_team2 > result.goals_team1)
        user_is_defender = user_id == result.team2.defender_user_id

    if user_is_defender:
        user_stats.games_played_defence += 1
        user_stats.games_won_defence += user_won * 1
    else:
        user_stats.games_played_offence += 1
        user_stats.games_won_offence += user_won * 1

    session.add(user_stats)
    session.commit()
    session.refresh(user_stats)
    return user_stats


def update_user_participant_stats_based_on_result(session: Session, result: ResultSubmission) -> List[UserStats]:
    updated_user_stats = []
    for user_id in result.match_participants:
        updated_user_stats.append(
            update_user_stats(session=session, result=result, user_id=user_id)
        )
    return updated_user_stats
