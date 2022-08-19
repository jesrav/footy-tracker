"""Services for working with user aggregated stats"""
from typing import List, Dict

from models.ranking import UserRanking
from models.rating import UserRating


def calculate_rankings(latest_user_ratings: List[UserRating], rating_type: str = 'overall') -> Dict[int, int]:
    """Get user rankings

    Either using `rating_type` "overall", "defence" or "offence".
    """
    if rating_type not in ["overall", "defence", "offence"]:
        raise ValueError("`rating_type` must be overall, defence or offence.")
    user_rankings = {}
    if rating_type == "overall":
        latest_user_ratings_sorted = sorted(latest_user_ratings, key=lambda x: x.overall_rating, reverse=True)
    elif rating_type == "defence":
        latest_user_ratings_sorted = sorted(latest_user_ratings, key=lambda x: x.rating_defence, reverse=True)
    else:
        latest_user_ratings_sorted = sorted(latest_user_ratings, key=lambda x: x.rating_offence, reverse=True)
    for i, user_rating in enumerate(latest_user_ratings_sorted, start=1):
        user_rankings[user_rating.user_id] = i
    return user_rankings


def get_updated_user_rankings(latest_user_ratings: List[UserRating]) -> List[UserRanking]:
    overall_rankings = calculate_rankings(latest_user_ratings, rating_type='overall')
    defensive_rankings = calculate_rankings(latest_user_ratings, rating_type='defence')
    offensive_rankings = calculate_rankings(latest_user_ratings, rating_type='offence')
    user_rankings = []
    for user_id, overall_ranking in overall_rankings.items():
        user_rankings.append(UserRanking(
            user_id=user_id,
            overall_ranking=overall_ranking,
            defensive_ranking=defensive_rankings[user_id],
            offensive_ranking=offensive_rankings[user_id],
        ))
    return user_rankings
