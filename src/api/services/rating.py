from typing import List

import elo

from models import team as team_models
from models import rating as rating_models

# User larger K-factor than the default
elo.K_FACTOR = 32

INITIAL_USER_RATING = 1200


def get_updated_elo_player_ratings(
        team1: team_models.Team, team2: team_models.Team, team1_goals: int, team2_goals: int
) -> List[rating_models.UserRatingCreate]:
    team1_rating = team1.defender.latest_rating.rating + team1.attacker.latest_rating.rating
    team2_rating = team2.defender.latest_rating.rating + team2.attacker.latest_rating.rating

    if team1_goals > team2_goals:
        new_team1_rating, new_team2_rating = elo.rate_1vs1(team1_rating, team2_rating)
    elif team1_goals < team2_goals:
        new_team2_rating, new_team1_rating = elo.rate_1vs1(team2_rating, team1_rating)
    else:
        new_team1_rating, new_team2_rating = team1_rating, team2_rating

    team1_rating_delta = new_team1_rating - team1_rating
    team2_rating_delta = new_team2_rating - team2_rating

    return [
        team1.defender.latest_rating.get_new_rating(rating_delta=team1_rating_delta),
        team1.attacker.latest_rating.get_new_rating(rating_delta=team1_rating_delta),
        team2.defender.latest_rating.get_new_rating(rating_delta=team2_rating_delta),
        team2.attacker.latest_rating.get_new_rating(rating_delta=team2_rating_delta),
    ]