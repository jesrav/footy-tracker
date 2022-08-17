from typing import List
from datetime import datetime

from sqlmodel import Session, select

from models.ranking import UserRanking
from services.ranking import get_updated_user_rankings
from crud.rating import get_latest_ratings


def get_user_rankings(session: Session) -> List[UserRanking]:
    statement = select(UserRanking)
    return session.exec(statement).all()


def update_user_rankings(session: Session) -> List[UserRanking]:
    statement = select(UserRanking)
    current_rankings = session.exec(statement).all()
    latest_user_ratings = get_latest_ratings(session=session)

    updated_user_rankings = get_updated_user_rankings(latest_user_ratings)

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
    session.commit()
    for user_ranking in updated_or_new_user_rankings:
        session.refresh(user_ranking)
    return updated_or_new_user_rankings
