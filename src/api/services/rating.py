"""Services for updating user rankings"""

INITIAL_USER_RATING = 1500
ELO_WIDTH = 400
K_FACTOR = 30

EGG_FACTOR = 1


async def elo_expected_result(elo_a, elo_b):
    """Classical elo expectation for result"""
    expect_a = 1.0/(1+10**((elo_b - elo_a)/ELO_WIDTH))
    return expect_a


async def update_ratings(winner_old_rating: float, looser_old_rating: float, winner_goals: int, looser_goals: int):
    """Update two ratings after a match result

    The update happens by an adjusted version of the ELO algorithm, that includes a bonus for giving the opponent
    an `egg` and rewards larger victories.
    """
    if winner_goals == 0:
        raise ValueError("Winner must have scored at least one goal.")
    if winner_goals <= looser_goals:
        raise ValueError("Winner must have more goals than looser.")
    expected_win = await elo_expected_result(winner_old_rating, looser_old_rating)
    result_is_egg = (looser_goals == 0)
    relative_goal_diff = (winner_goals - looser_goals) / winner_goals

    change_in_elo = K_FACTOR * (1 + EGG_FACTOR * result_is_egg) * relative_goal_diff * (1-expected_win)
    winner_old_rating += change_in_elo
    looser_old_rating -= change_in_elo
    return winner_old_rating, looser_old_rating


