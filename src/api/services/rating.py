"""Services for updating user rankings"""
from typing import List

from models import team as team_models
from models import rating as rating_models

INITIAL_USER_RATING = 1500
ELO_WIDTH = 400
K_FACTOR = 30

EGG_FACTOR = 1


def elo_expected_result(elo_a, elo_b):
    """Classical elo expectation for result"""
    expect_a = 1.0/(1+10**((elo_b - elo_a)/ELO_WIDTH))
    return expect_a


def update_ratings(winner_old_rating: float, looser_old_rating: float, winner_goals: int, looser_goals: int):
    """Update two ratings after a match result

    The update happens by an adjusted version of the ELO algorithm, that includes a bonus for giving the opponent
    an `egg` and rewards larger victories.
    """
    if winner_goals == 0:
        raise ValueError("Winner must have scored at least one goal.")
    if winner_goals <= looser_goals:
        raise ValueError("Winner must have more goals than looser.")
    expected_win = elo_expected_result(winner_old_rating, looser_old_rating)
    result_is_egg = (looser_goals == 0)
    relative_goal_diff = (winner_goals - looser_goals) / winner_goals

    change_in_elo = K_FACTOR * (1 + EGG_FACTOR * result_is_egg) * relative_goal_diff * (1-expected_win)
    winner_old_rating += change_in_elo
    looser_old_rating -= change_in_elo
    return winner_old_rating, looser_old_rating


def get_updated_player_ratings(
        team1: team_models.Team, team2: team_models.Team, team1_goals: int, team2_goals: int
) -> List[rating_models.UserRatingCreate]:

    team1_rating = team1.defender.latest_rating.rating_defence + team1.attacker.latest_rating.rating_offence
    team2_rating = team2.defender.latest_rating.rating_defence + team2.attacker.latest_rating.rating_offence

    if team1_goals > team2_goals:
        new_team1_rating, new_team2_rating = update_ratings(team1_rating, team2_rating, team1_goals, team2_goals)
    elif team1_goals < team2_goals:
        new_team2_rating, new_team1_rating = update_ratings(team2_rating, team1_rating, team2_goals, team1_goals)
    else:
        raise ValueError("There must be a winner. team1_goals ")

    team1_rating_delta = new_team1_rating - team1_rating
    team2_rating_delta = new_team2_rating - team2_rating

    return [
        team1.defender.latest_rating.get_new_rating(rating_delta_defence=team1_rating_delta),
        team1.attacker.latest_rating.get_new_rating(rating_delta_offence=team1_rating_delta),
        team2.defender.latest_rating.get_new_rating(rating_delta_defence=team2_rating_delta),
        team2.attacker.latest_rating.get_new_rating(rating_delta_offence=team2_rating_delta),
    ]
