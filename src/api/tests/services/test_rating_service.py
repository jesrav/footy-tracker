import pytest

from api.services.rating import update_ratings, elo_expected_result


@pytest.mark.asyncio
async def test_elo_expected_result():
    assert await elo_expected_result(1500, 1500) == 0.5, "Same reatings must give 0.5 elo probability"
    assert await elo_expected_result(2000, 1) == pytest.approx(1, abs=0.001), \
        "Elo probability must go to 1 when rating of first player is much larger"
    assert await elo_expected_result(1, 2000) == pytest.approx(0, abs=0.001), \
        "Elo probability must go to 0 when rating of second player is much larger"


@pytest.mark.asyncio
async def test_update_ratings_has_right_sign():
    # Test that player a gets a larger rating if he wins a gainst an equally rated player b.
    new_rating_a, new_rating_b = await update_ratings(1500, 1500, 10, 1)
    assert new_rating_a > new_rating_b, "Player a should have a higher rating after winning against equal player b."


@pytest.mark.asyncio
async def test_update_ratings_dependes_on_ratting():
    """Test that the size of the updates to the ratings are larger when the difference in rating is larger."""
    new_rating_a_1, new_rating_b_1 = await update_ratings(1500, 1400, 10, 1)
    rating_diff_a_1 = new_rating_a_1 - 1500

    new_rating_a_2, new_rating_b_2 = await update_ratings(1500, 1500, 10, 1)
    rating_diff_a_2 = new_rating_a_2 - 1500

    new_rating_a_3, new_rating_b_3 = await update_ratings(1500, 1600, 10, 1)
    rating_diff_a_3 = new_rating_a_3 - 1500

    assert rating_diff_a_1 < rating_diff_a_2 < rating_diff_a_3, "Rating difference should increase with rating difference."


@pytest.mark.asyncio
async def test_update_ratings_conserves_total_rating():
    """Test that the total rating is conserved when updating ratings."""
    new_rating_a, new_rating_b = await update_ratings(1500, 1500, 10, 1)
    assert new_rating_a + new_rating_b == 1500 + 1500, "Total rating should be conserved."


@pytest.mark.asyncio
async def test_update_ratings_dependence_on_goal_diff():
    """Test that a larger victory transfers more rating points."""
    goal_diffs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for i, goal_diff in enumerate(goal_diffs[:-1]):
        smaller_new_rating_a, _ = await update_ratings(1500, 1500, goal_diffs[i] + 1, 1)
        larger_new_rating_a, _ = await update_ratings(1500, 1500, goal_diffs[i+1] + 1, 1)
        assert larger_new_rating_a > smaller_new_rating_a, \
            "Player a should have a higher rating after winning with a larger goal difference."
